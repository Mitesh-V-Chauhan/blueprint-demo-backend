import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from models.schemas import (
    ChatRequest, ChatResponse, AgentContext, AgentType,
    MessageCreate, MessageResponse, StreamChunk
)
from services.database import Database
from agents.supervisor_agent import SupervisorAgent
from context.context_manager import ContextManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize supervisor agent
supervisor_agent = SupervisorAgent(api_key_index=1)
context_manager = ContextManager()

class WebSocketManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connection established: {connection_id}")
    
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def send_message(self, connection_id: str, message: dict):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                self.disconnect(connection_id)

ws_manager = WebSocketManager()

@router.post("/chat")
async def chat_with_supervisor(request: ChatRequest) -> ChatResponse:
    """Chat with supervisor agent"""
    try:
        logger.info(f"Chat request for project {request.project_id}: {request.message[:100]}...")
        
        # Verify project exists
        project = await Database.get_project(request.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get or create conversation context
        session_id = request.conversation_id or str(uuid.uuid4())
        context = await context_manager.get_or_create_context(
            project_id=request.project_id,
            user_id=project.user_id,
            session_id=session_id
        )
        
        # Add user message to context
        context.conversation_history.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save user message to database
        user_message = MessageCreate(
            content=request.message,
            role="user",
            project_id=request.project_id
        )
        await Database.create_message(user_message)
        
        # Execute supervisor agent
        response = await supervisor_agent.execute(context)
        
        # Extract actions taken and updated components
        actions_taken = []
        updated_components = []
        
        if response.tool_calls:
            for tool_call in response.tool_calls:
                actions_taken.append(tool_call.get("tool", "unknown_action"))
        
        # Determine what components might have been updated
        analysis = response.updated_context.project_data.get("analysis", {})
        if "flowchart" in analysis.get("agents_needed", []):
            updated_components.append("flowchart")
        if "overview" in analysis.get("action_plan", []):
            updated_components.append("overview")
        if "code" in analysis.get("action_plan", []):
            updated_components.append("code")
        
        # Add assistant message to context
        context.conversation_history.append({
            "role": "assistant",
            "content": response.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save assistant message to database
        assistant_message = MessageCreate(
            content=response.message,
            role="assistant",
            project_id=request.project_id
        )
        await Database.create_message(assistant_message)
        
        # Update conversation in context manager
        await context_manager.update_conversation(
            project_id=request.project_id,
            message=request.message,
            role="user"
        )
        await context_manager.update_conversation(
            project_id=request.project_id,
            message=response.message,
            role="assistant"
        )
        
        return ChatResponse(
            message=response.message,
            agent_type=AgentType.SUPERVISOR,
            actions_taken=actions_taken,
            updated_components=updated_components,
            conversation_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/chat/{project_id}")
async def websocket_chat(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time chat"""
    connection_id = str(uuid.uuid4())
    
    try:
        await ws_manager.connect(websocket, connection_id)
        
        # Verify project exists
        project = await Database.get_project(project_id)
        if not project:
            await websocket.send_json({
                "type": "error",
                "message": "Project not found"
            })
            return
        
        # Send connection confirmation
        await ws_manager.send_message(connection_id, {
            "type": "connected",
            "project_id": project_id,
            "connection_id": connection_id
        })
        
        # Create context for this WebSocket session
        session_id = str(uuid.uuid4())
        context = await context_manager.get_or_create_context(
            project_id=project_id,
            user_id=project.user_id,
            session_id=session_id
        )
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "chat":
                message_content = data.get("message", "")
                
                if not message_content.strip():
                    continue
                
                # Send typing indicator
                await ws_manager.send_message(connection_id, {
                    "type": "typing",
                    "agent": "supervisor"
                })
                
                try:
                    # Add user message to context
                    context.conversation_history.append({
                        "role": "user",
                        "content": message_content,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Save user message
                    user_message = MessageCreate(
                        content=message_content,
                        role="user",
                        project_id=project_id
                    )
                    await Database.create_message(user_message)
                    
                    # Execute supervisor agent
                    response = await supervisor_agent.execute(context)
                    
                    # Add assistant message to context
                    context.conversation_history.append({
                        "role": "assistant",
                        "content": response.message,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Save assistant message
                    assistant_message = MessageCreate(
                        content=response.message,
                        role="assistant",
                        project_id=project_id
                    )
                    await Database.create_message(assistant_message)
                    
                    # Send response to client
                    await ws_manager.send_message(connection_id, {
                        "type": "response",
                        "message": response.message,
                        "agent_type": "supervisor",
                        "confidence": response.confidence,
                        "actions_taken": [tool.get("tool", "unknown") for tool in response.tool_calls],
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Update context manager
                    await context_manager.save_context(context)
                    
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")
                    await ws_manager.send_message(connection_id, {
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    })
            
            elif message_type == "ping":
                await ws_manager.send_message(connection_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ws_manager.disconnect(connection_id)

@router.get("/conversation/{project_id}")
async def get_conversation_history(project_id: str, limit: int = 50) -> List[MessageResponse]:
    """Get conversation history for a project"""
    try:
        # Verify project exists
        project = await Database.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get messages from database
        messages = await Database.get_project_messages(project_id, limit)
        
        return messages
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/{project_id}")
async def clear_conversation_history(project_id: str):
    """Clear conversation history for a project"""
    try:
        # Verify project exists
        project = await Database.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Clear from context manager
        await context_manager.clear_project_context(project_id)
        
        # Note: You'd also want to clear messages from database
        # This would require implementing a delete messages method
        
        return {"message": "Conversation history cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat-stats/{project_id}")
async def get_chat_statistics(project_id: str):
    """Get chat statistics for a project"""
    try:
        # Verify project exists
        project = await Database.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get context stats
        context_stats = await context_manager.get_context_stats(project_id)
        
        # Get message count from database
        messages = await Database.get_project_messages(project_id, 1000)  # Get more for counting
        
        # Calculate statistics
        user_messages = len([m for m in messages if m.role == "user"])
        assistant_messages = len([m for m in messages if m.role == "assistant"])
        
        return {
            "project_id": project_id,
            "total_messages": len(messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "context_stats": context_stats,
            "last_activity": messages[0].created_at if messages else None
        }
        
    except Exception as e:
        logger.error(f"Error getting chat stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/bulk-process")
async def bulk_process_messages(request: Dict[str, Any]):
    """Process multiple messages in batch (for testing or migration)"""
    try:
        project_id = request.get("project_id")
        messages = request.get("messages", [])
        
        if not project_id or not messages:
            raise HTTPException(status_code=400, detail="Missing project_id or messages")
        
        # Verify project exists
        project = await Database.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        processed_messages = []
        
        for msg_data in messages:
            try:
                message = MessageCreate(
                    content=msg_data.get("content", ""),
                    role=msg_data.get("role", "user"),
                    project_id=project_id
                )
                saved_message = await Database.create_message(message)
                processed_messages.append(saved_message)
                
                # Update context manager
                await context_manager.update_conversation(
                    project_id=project_id,
                    message=msg_data.get("content", ""),
                    role=msg_data.get("role", "user"),
                    save_to_context=False  # Don't update active contexts for bulk processing
                )
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue
        
        return {
            "processed_count": len(processed_messages),
            "total_requested": len(messages),
            "project_id": project_id
        }
        
    except Exception as e:
        logger.error(f"Error in bulk processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))