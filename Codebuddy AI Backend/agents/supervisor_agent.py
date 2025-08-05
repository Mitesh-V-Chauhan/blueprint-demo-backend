import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

from agents.base_agent import BaseAgent, AgentExecutor
from models.schemas import AgentType, AgentContext, AgentResponse
from rag.vector_store import VectorStore
from services.database import Database

logger = logging.getLogger(__name__)

class SupervisorAgent(BaseAgent):
    """Supervisor agent that orchestrates other agents and handles complex queries"""
    
    def __init__(self, api_key_index: int = 1):
        super().__init__(AgentType.SUPERVISOR, api_key_index)
        self.executor = AgentExecutor()
        self._setup_tools()
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Define supervisor-specific tools"""
        return [
            {
                "name": "analyze_user_intent",
                "description": "Analyze user message to determine intent and required actions",
                "parameters": {
                    "message": "str",
                    "context": "dict"
                }
            },
            {
                "name": "delegate_to_agent",
                "description": "Delegate task to specific agent",
                "parameters": {
                    "agent_type": "str",
                    "task_description": "str",
                    "context": "dict"
                }
            },
            {
                "name": "update_project_component",
                "description": "Update specific project component (overview, flowchart, code)",
                "parameters": {
                    "component_type": "str",
                    "updates": "dict",
                    "project_id": "str"
                }
            },
            {
                "name": "search_knowledge_base",
                "description": "Search project knowledge base for relevant information",
                "parameters": {
                    "query": "str",
                    "project_id": "str",
                    "doc_types": "list"
                }
            },
            {
                "name": "coordinate_multi_agent_task",
                "description": "Coordinate task across multiple agents",
                "parameters": {
                    "task_type": "str",
                    "agents_required": "list",
                    "context": "dict"
                }
            }
        ]
    
    def _get_system_prompt(self) -> str:
        """Get supervisor system prompt"""
        return """You are the Supervisor Agent for an AI Blueprint Generator system. Your role is to:

1. ANALYZE user requests and determine the best approach
2. DELEGATE tasks to appropriate specialist agents
3. COORDINATE multi-agent workflows
4. UPDATE project components based on user feedback
5. MAINTAIN context and consistency across all operations

Available Agents:
- REQUIREMENTS: Analyzes project requirements and asks clarifying questions
- ARCHITECT: Designs technical architecture and recommends tech stacks
- DESIGNER: Creates flowcharts and visual representations
- WRITER: Generates documentation and explanations
- CODE_GENERATOR: Creates code files and project structure
- ANALYZER: Analyzes existing codebases

Your Capabilities:
- Understand user intent from natural language
- Route requests to appropriate agents
- Update specific project components
- Search and utilize project knowledge base
- Coordinate complex multi-step tasks
- Maintain conversation context

Response Format:
Always respond with a JSON object containing:
{
    "intent": "description of user intent",
    "action_plan": ["step1", "step2", "step3"],
    "agents_needed": ["agent1", "agent2"],
    "immediate_response": "response to user",
    "tool_calls": [{"tool": "tool_name", "parameters": {...}}],
    "confidence": 0.8
}

Rules:
1. If user wants to modify flowchart, also update overview and potentially code
2. Always search knowledge base before making changes
3. Maintain consistency across all project components
4. Provide clear explanations for all actions
5. Ask for clarification when intent is ambiguous
"""
    
    def _setup_tools(self):
        """Setup supervisor-specific tools"""
        self.tool_functions = {
            "analyze_user_intent": self._analyze_user_intent,
            "delegate_to_agent": self._delegate_to_agent,
            "update_project_component": self._update_project_component,
            "search_knowledge_base": self._search_knowledge_base,
            "coordinate_multi_agent_task": self._coordinate_multi_agent_task
        }
    
    async def _process_request(self, context: AgentContext) -> Dict[str, Any]:
        """Process supervisor request"""
        try:
            # Get the latest user message
            last_message = context.conversation_history[-1] if context.conversation_history else {}
            user_message = last_message.get('content', '')
            
            if not user_message:
                return {
                    "message": "No message to process",
                    "action_taken": "none",
                    "error": "Empty message"
                }
            
            # Build the prompt with context
            context_prompt = self._build_context_prompt(context)
            
            # Create messages for LLM
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=f"""
Context:
{context_prompt}

User Request: "{user_message}"

Analyze this request and provide a detailed action plan.
""")
            ]
            
            # Get supervisor's analysis
            response = await self._invoke_llm(messages)
            analysis = self._extract_json_from_response(response)
            
            if not analysis:
                # Fallback analysis
                analysis = await self._fallback_analysis(user_message, context)
            
            # Execute the action plan
            execution_result = await self._execute_action_plan(analysis, context)
            
            return {
                "message": execution_result.get("response", analysis.get("immediate_response", "Task completed")),
                "action_taken": f"Analyzed intent: {analysis.get('intent', 'unknown')}",
                "tool_calls": analysis.get('tool_calls', []),
                "analysis": analysis,
                "execution_result": execution_result
            }
            
        except Exception as e:
            logger.error(f"Error processing supervisor request: {e}")
            return {
                "message": f"Error processing request: {str(e)}",
                "action_taken": "error_handling",
                "error": str(e)
            }
    
    async def _fallback_analysis(self, user_message: str, context: AgentContext) -> Dict[str, Any]:
        """Fallback analysis when JSON extraction fails"""
        # Simple keyword-based analysis
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['change', 'modify', 'update', 'edit']):
            if any(word in message_lower for word in ['flowchart', 'diagram', 'architecture']):
                return {
                    "intent": "modify_flowchart",
                    "action_plan": ["search_knowledge", "update_flowchart", "update_overview"],
                    "agents_needed": ["DESIGNER", "WRITER"],
                    "immediate_response": "I'll help you modify the flowchart and update related components.",
                    "confidence": 0.7
                }
            elif any(word in message_lower for word in ['code', 'file', 'implementation']):
                return {
                    "intent": "modify_code",
                    "action_plan": ["search_knowledge", "update_code", "update_explanation"],
                    "agents_needed": ["CODE_GENERATOR", "WRITER"],
                    "immediate_response": "I'll help you modify the code and update related documentation.",
                    "confidence": 0.7
                }
        
        elif any(word in message_lower for word in ['explain', 'what', 'how', 'why']):
            return {
                "intent": "explain_project",
                "action_plan": ["search_knowledge", "provide_explanation"],
                "agents_needed": ["WRITER"],
                "immediate_response": "Let me search the project knowledge base and provide an explanation.",
                "confidence": 0.8
            }
        
        # Default fallback
        return {
            "intent": "general_assistance",
            "action_plan": ["search_knowledge", "provide_general_help"],
            "agents_needed": ["WRITER"],
            "immediate_response": "I'll help you with your request. Let me search for relevant information.",
            "confidence": 0.6
        }
    
    async def _execute_action_plan(self, analysis: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute the action plan"""
        try:
            action_plan = analysis.get("action_plan", [])
            agents_needed = analysis.get("agents_needed", [])
            tool_calls = analysis.get("tool_calls", [])
            
            execution_results = []
            
            # Execute tool calls first
            for tool_call in tool_calls:
                tool_name = tool_call.get("tool")
                parameters = tool_call.get("parameters", {})
                
                if tool_name in self.tool_functions:
                    try:
                        result = await self.tool_functions[tool_name](**parameters)
                        execution_results.append({
                            "tool": tool_name,
                            "result": result,
                            "success": True
                        })
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_name}: {e}")
                        execution_results.append({
                            "tool": tool_name,
                            "error": str(e),
                            "success": False
                        })
            
            # Execute agent delegation if needed
            agent_responses = []
            for agent_type_str in agents_needed:
                try:
                    agent_type = AgentType(agent_type_str.lower())
                    if agent_type in self.executor.agents:
                        response = await self.executor.execute_agent(agent_type, context)
                        agent_responses.append({
                            "agent": agent_type_str,
                            "response": response.message,
                            "success": True
                        })
                except Exception as e:
                    logger.error(f"Error executing agent {agent_type_str}: {e}")
                    agent_responses.append({
                        "agent": agent_type_str,
                        "error": str(e),
                        "success": False
                    })
            
            # Compile final response
            response_parts = [analysis.get("immediate_response", "")]
            
            for result in execution_results:
                if result["success"]:
                    response_parts.append(f"✓ {result['tool']} completed successfully")
                else:
                    response_parts.append(f"✗ {result['tool']} failed: {result.get('error', 'Unknown error')}")
            
            for response in agent_responses:
                if response["success"]:
                    response_parts.append(f"✓ {response['agent']}: {response['response']}")
                else:
                    response_parts.append(f"✗ {response['agent']} failed: {response.get('error', 'Unknown error')}")
            
            return {
                "response": "\n\n".join(response_parts),
                "tool_results": execution_results,
                "agent_responses": agent_responses,
                "success": all(r.get("success", False) for r in execution_results + agent_responses)
            }
            
        except Exception as e:
            logger.error(f"Error executing action plan: {e}")
            return {
                "response": f"Error executing action plan: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    # Tool implementations
    async def _analyze_user_intent(self, message: str, context: dict) -> Dict[str, Any]:
        """Analyze user intent"""
        # This is handled in the main processing logic
        return {"intent": "analyzed", "message": message}
    
    async def _delegate_to_agent(self, agent_type: str, task_description: str, context: dict) -> Dict[str, Any]:
        """Delegate task to specific agent"""
        try:
            agent_enum = AgentType(agent_type.lower())
            if agent_enum in self.executor.agents:
                # Create context for the agent
                agent_context = AgentContext(**context)
                agent_context.conversation_history.append({
                    "role": "user",
                    "content": task_description
                })
                
                response = await self.executor.execute_agent(agent_enum, agent_context)
                return {
                    "success": True,
                    "agent": agent_type,
                    "response": response.message
                }
            else:
                return {
                    "success": False,
                    "error": f"Agent {agent_type} not available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _update_project_component(self, component_type: str, updates: dict, project_id: str) -> Dict[str, Any]:
        """Update specific project component"""
        try:
            if component_type == "overview":
                return await self._update_overview(project_id, updates)
            elif component_type == "flowchart":
                return await self._update_flowchart(project_id, updates)
            elif component_type == "code":
                return await self._update_code_files(project_id, updates)
            else:
                return {
                    "success": False,
                    "error": f"Unknown component type: {component_type}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _search_knowledge_base(self, query: str, project_id: str, doc_types: list = None) -> Dict[str, Any]:
        """Search project knowledge base"""
        try:
            results = await self.vector_store.search_project_knowledge(
                project_id=project_id,
                query=query,
                doc_types=doc_types,
                limit=5
            )
            
            return {
                "success": True,
                "results": results,
                "query": query
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _coordinate_multi_agent_task(self, task_type: str, agents_required: list, context: dict) -> Dict[str, Any]:
        """Coordinate multi-agent task"""
        try:
            agent_types = [AgentType(agent.lower()) for agent in agents_required]
            agent_context = AgentContext(**context)
            
            responses = await self.executor.execute_workflow(agent_types, agent_context)
            
            return {
                "success": True,
                "task_type": task_type,
                "responses": [r.message for r in responses]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Helper methods for updating components
    async def _update_overview(self, project_id: str, updates: dict) -> Dict[str, Any]:
        """Update project overview"""
        try:
            current_overview = await Database.get_project_overview(project_id)
            if not current_overview:
                return {"success": False, "error": "Overview not found"}
            
            # Update database
            updated_overview = await Database.update_project_overview(
                project_id=project_id,
                content=updates.get("content"),
                user_flow=updates.get("user_flow"),
                tech_stack=updates.get("tech_stack")
            )
            
            # Update vector store
            if updated_overview:
                await VectorStore.add_project_overview(
                    project_id=project_id,
                    content=updated_overview.content,
                    tech_stack=updated_overview.tech_stack,
                    user_flow=updated_overview.user_flow
                )
            
            return {
                "success": True,
                "message": "Overview updated successfully"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _update_flowchart(self, project_id: str, updates: dict) -> Dict[str, Any]:
        """Update flowchart"""
        try:
            from models.schemas import FlowchartStateCreate, FlowchartData
            
            flowchart_data = FlowchartData(**updates.get("flowchart_json", {}))
            flowchart_state = FlowchartStateCreate(
                flowchart_json=flowchart_data,
                change_description=updates.get("change_description", "Supervisor update"),
                project_id=project_id
            )
            
            # Save to database
            saved_flowchart = await Database.create_flowchart_state(flowchart_state)
            
            # Update vector store
            await VectorStore.add_flowchart_data(
                project_id=project_id,
                flowchart_json=flowchart_data.dict(),
                description=flowchart_state.change_description
            )
            
            return {
                "success": True,
                "message": "Flowchart updated successfully",
                "flowchart_id": saved_flowchart.id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _update_code_files(self, project_id: str, updates: dict) -> Dict[str, Any]:
        """Update code files"""
        try:
            updated_files = []
            
            for file_update in updates.get("files", []):
                file_id = file_update.get("file_id")
                if file_id:
                    updated_file = await Database.update_file_node(
                        file_id=file_id,
                        generated_code=file_update.get("generated_code"),
                        explanation=file_update.get("explanation")
                    )
                    if updated_file:
                        updated_files.append(updated_file.path)
                        
                        # Update vector store
                        await VectorStore.add_code_file(
                            project_id=project_id,
                            file_path=updated_file.path,
                            content=updated_file.generated_code or "",
                            explanation=updated_file.explanation or ""
                        )
            
            return {
                "success": True,
                "message": f"Updated {len(updated_files)} code files",
                "updated_files": updated_files
            }
        except Exception as e:
            return {"success": False, "error": str(e)}