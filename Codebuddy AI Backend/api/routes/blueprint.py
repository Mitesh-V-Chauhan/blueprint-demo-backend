import logging
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models.schemas import (
    BlueprintRequest, ProjectCreate, ProjectResponse,
    AgentContext, AgentType, StreamChunk, ErrorResponse,
    ClarifyingQuestion, TechStackRecommendation, FlowchartData,
    ProjectOverviewCreate, FlowchartStateCreate, FileNodeCreate
)
from services.database import Database
from agents.supervisor_agent import SupervisorAgent
from agents.requirements_agent import RequirementsAgent
from agents.architect_agent import ArchitectAgent
from agents.designer_agent import DesignerAgent
from agents.writer_agent import WriterAgent
from agents.code_generator_agent import CodeGeneratorAgent
from context.context_manager import ContextManager
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize agents
supervisor_agent = SupervisorAgent(api_key_index=1)
requirements_agent = RequirementsAgent(api_key_index=2)
architect_agent = ArchitectAgent(api_key_index=3)
designer_agent = DesignerAgent(api_key_index=4)
writer_agent = WriterAgent(api_key_index=5)
code_generator_agent = CodeGeneratorAgent(api_key_index=6)

# Register agents with supervisor
supervisor_agent.executor.register_agent(requirements_agent)
supervisor_agent.executor.register_agent(architect_agent)
supervisor_agent.executor.register_agent(designer_agent)
supervisor_agent.executor.register_agent(writer_agent)
supervisor_agent.executor.register_agent(code_generator_agent)

context_manager = ContextManager()

class GenerationState(BaseModel):
    project_id: str
    user_id: str
    session_id: str
    current_step: str
    progress: int
    status: str
    results: Dict[str, Any] = {}

# In-memory storage for generation states (in production, use Redis)
generation_states: Dict[str, GenerationState] = {}

@router.post("/generate-questions")
async def generate_clarifying_questions(request: BlueprintRequest) -> List[ClarifyingQuestion]:
    """Generate clarifying questions for a project idea"""
    try:
        logger.info(f"Generating questions for idea: {request.initial_idea[:100]}...")
        
        # Create context
        session_id = str(uuid.uuid4())
        context = AgentContext(
            project_id="temp",
            user_id="temp",
            session_id=session_id,
            current_step="requirements",
            conversation_history=[{
                "role": "user",
                "content": request.initial_idea
            }],
            project_data={
                "initial_idea": request.initial_idea,
                "user_profile": request.user_profile.dict(),
                "project_type": request.project_type.value
            }
        )
        
        # Execute requirements agent
        response = await requirements_agent.execute(context)
        
        if response.confidence < 0.5:
            raise HTTPException(status_code=500, detail="Failed to generate quality questions")
        
        # Extract questions from response
        questions_data = response.updated_context.project_data.get("clarifying_questions", [])
        
        questions = []
        for i, q in enumerate(questions_data[:3]):  # Limit to 3 questions
            questions.append(ClarifyingQuestion(
                question=q,
                context=f"Question {i+1} of 3"
            ))
        
        return questions
        
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-blueprint")
async def generate_blueprint(request: BlueprintRequest, background_tasks: BackgroundTasks):
    """Generate complete blueprint with streaming response"""
    try:
        logger.info(f"Starting blueprint generation for: {request.initial_idea[:100]}...")
        
        # Create project in database
        project_create = ProjectCreate(
            name=request.initial_idea[:100] + "..." if len(request.initial_idea) > 100 else request.initial_idea,
            user_input=request.initial_idea,
            type=request.project_type,
            repo_url=request.repo_url
        )
        
        # For now, use a temporary user ID (in production, get from auth)
        user_id = "temp_user"
        project = await Database.create_project(project_create, user_id)
        
        # Create generation session
        session_id = str(uuid.uuid4())
        generation_state = GenerationState(
            project_id=project.id,
            user_id=user_id,
            session_id=session_id,
            current_step="starting",
            progress=0,
            status="initializing"
        )
        generation_states[session_id] = generation_state
        
        # Start background generation
        background_tasks.add_task(
            _generate_blueprint_background,
            project.id,
            user_id,
            session_id,
            request
        )
        
        # Return streaming response
        return StreamingResponse(
            _stream_generation_progress(session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"Error starting blueprint generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _stream_generation_progress(session_id: str):
    """Stream generation progress to client"""
    try:
        max_wait = 300  # 5 minutes
        wait_time = 0
        
        while wait_time < max_wait:
            if session_id not in generation_states:
                break
            
            state = generation_states[session_id]
            
            # Send progress update
            chunk = StreamChunk(
                type="progress",
                data={
                    "step": state.current_step,
                    "progress": state.progress,
                    "status": state.status,
                    "session_id": session_id
                }
            )
            
            yield f"data: {chunk.json()}\n\n"
            
            # Send results if available
            if state.results:
                result_chunk = StreamChunk(
                    type="result",
                    data=state.results
                )
                yield f"data: {result_chunk.json()}\n\n"
                state.results = {}  # Clear sent results
            
            # Check if complete
            if state.status == "completed":
                completion_chunk = StreamChunk(
                    type="complete",
                    data={
                        "project_id": state.project_id,
                        "message": "Blueprint generation completed successfully!"
                    }
                )
                yield f"data: {completion_chunk.json()}\n\n"
                break
            
            if state.status == "error":
                error_chunk = StreamChunk(
                    type="error",
                    data={"message": "Blueprint generation failed"}
                )
                yield f"data: {error_chunk.json()}\n\n"
                break
            
            await asyncio.sleep(2)
            wait_time += 2
        
        # Cleanup
        if session_id in generation_states:
            del generation_states[session_id]
            
    except Exception as e:
        logger.error(f"Error streaming progress: {e}")
        error_chunk = StreamChunk(
            type="error",
            data={"message": f"Streaming error: {str(e)}"}
        )
        yield f"data: {error_chunk.json()}\n\n"

async def _generate_blueprint_background(project_id: str, user_id: str, 
                                       session_id: str, request: BlueprintRequest):
    """Background task for blueprint generation"""
    try:
        state = generation_states[session_id]
        
        # Create context
        context = AgentContext(
            project_id=project_id,
            user_id=user_id,
            session_id=session_id,
            current_step="requirements",
            conversation_history=[{
                "role": "user",
                "content": request.initial_idea
            }],
            project_data={
                "initial_idea": request.initial_idea,
                "user_profile": request.user_profile.dict(),
                "user_answers": request.user_answers,
                "project_type": request.project_type.value
            }
        )
        
        # Build full context
        if request.user_answers:
            qa_text = "\n".join(f"Q{i+1}: {ans}" for i, ans in enumerate(request.user_answers))
            full_context = f"""
Project Idea: {request.initial_idea}

User Profile:
- Name: {request.user_profile.name}
- Experience: {request.user_profile.experience_level}

User Clarifications:
{qa_text}
            """.strip()
        else:
            full_context = f"""
Project Idea: {request.initial_idea}
User Profile: {request.user_profile.name} ({request.user_profile.experience_level})
            """.strip()
        
        context.project_data["full_context"] = full_context
        
        # Step 1: Architecture Analysis
        state.current_step = "architecture"
        state.progress = 20
        state.status = "analyzing"
        
        arch_response = await architect_agent.execute(context)
        context = arch_response.updated_context
        
        state.results["tech_stack"] = context.project_data.get("tech_stack", {})
        state.progress = 40
        
        # Step 2: Design Generation
        state.current_step = "design"
        state.status = "designing"
        
        design_response = await designer_agent.execute(context)
        context = design_response.updated_context
        
        # Save flowchart to database
        flowchart_data = context.project_data.get("flowchart", {})
        if flowchart_data:
            try:
                flowchart_state = FlowchartStateCreate(
                    flowchart_json=FlowchartData(**flowchart_data),
                    change_description="Initial generation",
                    project_id=project_id
                )
                await Database.create_flowchart_state(flowchart_state)
            except Exception as e:
                logger.error(f"Error saving flowchart: {e}")
        
        state.results["flowchart"] = flowchart_data
        state.progress = 60
        
        # Step 3: Documentation
        state.current_step = "documentation"
        state.status = "writing"
        
        writer_response = await writer_agent.execute(context)
        context = writer_response.updated_context
        
        # Save project overview
        overview_content = context.project_data.get("project_overview", "")
        if overview_content:
            try:
                overview = ProjectOverviewCreate(
                    content=overview_content,
                    user_flow=context.project_data.get("user_flow", ""),
                    tech_stack=context.project_data.get("tech_stack", {}),
                    project_id=project_id
                )
                await Database.create_project_overview(overview)
            except Exception as e:
                logger.error(f"Error saving overview: {e}")
        
        state.results["overview"] = overview_content
        state.progress = 80
        
        # Step 4: Code Generation
        state.current_step = "code_generation"
        state.status = "generating_code"
        
        code_response = await code_generator_agent.execute(context)
        context = code_response.updated_context
        
        # Save file structure
        files_data = context.project_data.get("files", [])
        saved_files = []
        
        for file_data in files_data:
            try:
                file_node = FileNodeCreate(
                    name=file_data.get("fileName", "unknown"),
                    path=file_data.get("fileName", "unknown"),
                    type="FILE",  # Assuming all generated are files
                    generated_code=file_data.get("code", ""),
                    explanation=file_data.get("explanation", ""),
                    project_id=project_id
                )
                saved_file = await Database.create_file_node(file_node)
                saved_files.append({
                    "id": saved_file.id,
                    "name": saved_file.name,
                    "path": saved_file.path,
                    "code": saved_file.generated_code,
                    "explanation": saved_file.explanation
                })
            except Exception as e:
                logger.error(f"Error saving file {file_data.get('fileName')}: {e}")
        
        state.results["files"] = saved_files
        state.progress = 95
        
        # Step 5: RAG Integration
        state.current_step = "indexing"
        state.status = "finalizing"
        
        # Add to vector store
        try:
            # Add overview
            if overview_content:
                await VectorStore.add_project_overview(
                    project_id=project_id,
                    content=overview_content,
                    tech_stack=context.project_data.get("tech_stack", {}),
                    user_flow=context.project_data.get("user_flow", "")
                )
            
            # Add flowchart
            if flowchart_data:
                await VectorStore.add_flowchart_data(
                    project_id=project_id,
                    flowchart_json=flowchart_data,
                    description="Initial architecture diagram"
                )
            
            # Add code files
            for file_data in saved_files:
                await VectorStore.add_code_file(
                    project_id=project_id,
                    file_path=file_data["path"],
                    content=file_data["code"],
                    explanation=file_data["explanation"]
                )
            
            # Add conversation context
            await VectorStore.add_conversation_context(
                project_id=project_id,
                conversation=context.conversation_history
            )
            
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")
        
        # Complete
        state.current_step = "completed"
        state.progress = 100
        state.status = "completed"
        state.results["project_id"] = project_id
        
        logger.info(f"Blueprint generation completed for project {project_id}")
        
    except Exception as e:
        logger.error(f"Error in background generation: {e}")
        if session_id in generation_states:
            generation_states[session_id].status = "error"
            generation_states[session_id].results = {"error": str(e)}

@router.get("/generation-status/{session_id}")
async def get_generation_status(session_id: str):
    """Get current generation status"""
    if session_id not in generation_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = generation_states[session_id]
    return {
        "session_id": session_id,
        "project_id": state.project_id,
        "current_step": state.current_step,
        "progress": state.progress,
        "status": state.status,
        "results": state.results
    }

@router.get("/project/{project_id}")
async def get_project_details(project_id: str):
    """Get complete project details"""
    try:
        # Get project
        project = await Database.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get overview
        overview = await Database.get_project_overview(project_id)
        
        # Get latest flowchart
        flowchart = await Database.get_latest_flowchart(project_id)
        
        # Get file structure
        files = await Database.get_project_file_structure(project_id)
        
        # Get conversation history
        messages = await Database.get_project_messages(project_id)
        
        return {
            "project": project,
            "overview": overview,
            "flowchart": flowchart,
            "files": files,
            "messages": messages,
            "metadata": {
                "total_files": len(files),
                "total_messages": len(messages),
                "last_updated": project.updated_at
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting project details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/project/{project_id}")
async def delete_project(project_id: str):
    """Delete a project and all associated data"""
    try:
        # Verify project exists
        project = await Database.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete from vector store
        await VectorStore.delete_project_data(project_id)
        
        # Clear context
        await context_manager.clear_project_context(project_id)
        
        # Database deletion is handled by CASCADE in schema
        # Just delete the main project record
        # Note: You'd need to implement this in Database class
        
        return {"message": "Project deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))