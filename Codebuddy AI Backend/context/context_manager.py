import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import redis.asyncio as redis

from utils.config import Settings
from models.schemas import AgentContext

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages context storage and retrieval across agent sessions"""
    
    _redis_client: Optional[redis.Redis] = None
    _settings: Settings = Settings()
    
    @classmethod
    async def initialize(cls):
        """Initialize Redis connection"""
        try:
            cls._redis_client = redis.from_url(
                cls._settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await cls._redis_client.ping()
            logger.info("Context manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize context manager: {e}")
            raise
    
    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._redis_client:
            await cls._redis_client.close()
            logger.info("Context manager connection closed")
    
    @classmethod
    async def health_check(cls) -> str:
        """Check context manager health"""
        try:
            await cls._redis_client.ping()
            return "healthy"
        except Exception as e:
            logger.error(f"Context manager health check failed: {e}")
            return f"unhealthy: {e}"
    
    @classmethod
    def _get_context_key(cls, project_id: str, session_id: str) -> str:
        """Generate Redis key for context"""
        return f"context:{project_id}:{session_id}"
    
    @classmethod
    def _get_session_key(cls, project_id: str) -> str:
        """Generate Redis key for session list"""
        return f"sessions:{project_id}"
    
    @classmethod
    def _get_conversation_key(cls, project_id: str) -> str:
        """Generate Redis key for conversation history"""
        return f"conversation:{project_id}"
    
    async def save_context(self, context: AgentContext, ttl: int = 3600) -> bool:
        """Save agent context to Redis"""
        try:
            context_key = self._get_context_key(context.project_id, context.session_id)
            
            # Serialize context
            context_data = {
                "project_id": context.project_id,
                "user_id": context.user_id,
                "session_id": context.session_id,
                "current_step": context.current_step,
                "conversation_history": context.conversation_history,
                "project_data": context.project_data,
                "rag_context": context.rag_context,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to Redis with TTL
            await self._redis_client.setex(
                context_key,
                ttl,
                json.dumps(context_data, default=str)
            )
            
            # Add session to session list
            session_key = self._get_session_key(context.project_id)
            await self._redis_client.sadd(session_key, context.session_id)
            await self._redis_client.expire(session_key, ttl)
            
            logger.info(f"Saved context for project {context.project_id}, session {context.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
            return False
    
    async def load_context(self, project_id: str, session_id: str) -> Optional[AgentContext]:
        """Load agent context from Redis"""
        try:
            context_key = self._get_context_key(project_id, session_id)
            context_data = await self._redis_client.get(context_key)
            
            if not context_data:
                logger.warning(f"No context found for project {project_id}, session {session_id}")
                return None
            
            # Deserialize context
            data = json.loads(context_data)
            
            context = AgentContext(
                project_id=data["project_id"],
                user_id=data["user_id"],
                session_id=data["session_id"],
                current_step=data.get("current_step", ""),
                conversation_history=data.get("conversation_history", []),
                project_data=data.get("project_data", {}),
                rag_context=data.get("rag_context", [])
            )
            
            logger.info(f"Loaded context for project {project_id}, session {session_id}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to load context: {e}")
            return None
    
    async def get_or_create_context(self, project_id: str, user_id: str, 
                                  session_id: str) -> AgentContext:
        """Get existing context or create new one"""
        context = await self.load_context(project_id, session_id)
        
        if context is None:
            # Create new context
            context = AgentContext(
                project_id=project_id,
                user_id=user_id,
                session_id=session_id,
                current_step="",
                conversation_history=[],
                project_data={},
                rag_context=[]
            )
            
            # Load existing conversation history if available
            conversation = await self.get_conversation_history(project_id)
            if conversation:
                context.conversation_history = conversation[-20:]  # Last 20 messages
            
            logger.info(f"Created new context for project {project_id}, session {session_id}")
        
        return context
    
    async def update_conversation(self, project_id: str, message: str, 
                                role: str, save_to_context: bool = True) -> bool:
        """Update conversation history"""
        try:
            conversation_key = self._get_conversation_key(project_id)
            
            # Create message entry
            message_entry = {
                "role": role,
                "content": message,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to conversation list
            await self._redis_client.lpush(
                conversation_key,
                json.dumps(message_entry)
            )
            
            # Keep only last 100 messages
            await self._redis_client.ltrim(conversation_key, 0, 99)
            
            # Set expiry (24 hours)
            await self._redis_client.expire(conversation_key, 86400)
            
            # Update all active contexts if requested
            if save_to_context:
                await self._update_active_contexts(project_id, message_entry)
            
            logger.info(f"Updated conversation for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation: {e}")
            return False
    
    async def get_conversation_history(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history"""
        try:
            conversation_key = self._get_conversation_key(project_id)
            
            # Get messages (latest first)
            messages = await self._redis_client.lrange(conversation_key, 0, limit - 1)
            
            # Parse and reverse (oldest first)
            conversation = []
            for msg in reversed(messages):
                try:
                    conversation.append(json.loads(msg))
                except json.JSONDecodeError:
                    continue
            
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    async def _update_active_contexts(self, project_id: str, message_entry: Dict[str, Any]):
        """Update all active contexts with new message"""
        try:
            session_key = self._get_session_key(project_id)
            sessions = await self._redis_client.smembers(session_key)
            
            for session_id in sessions:
                context = await self.load_context(project_id, session_id)
                if context:
                    context.conversation_history.append(message_entry)
                    # Keep only last 20 messages in context
                    context.conversation_history = context.conversation_history[-20:]
                    await self.save_context(context)
            
        except Exception as e:
            logger.error(f"Failed to update active contexts: {e}")
    
    async def clear_project_context(self, project_id: str) -> bool:
        """Clear all context data for a project"""
        try:
            # Get all sessions for the project
            session_key = self._get_session_key(project_id)
            sessions = await self._redis_client.smembers(session_key)
            
            # Delete all context keys
            keys_to_delete = [session_key]
            for session_id in sessions:
                context_key = self._get_context_key(project_id, session_id)
                keys_to_delete.append(context_key)
            
            # Add conversation key
            conversation_key = self._get_conversation_key(project_id)
            keys_to_delete.append(conversation_key)
            
            # Delete all keys
            if keys_to_delete:
                await self._redis_client.delete(*keys_to_delete)
            
            logger.info(f"Cleared all context data for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear project context: {e}")
            return False
    
    async def get_project_sessions(self, project_id: str) -> List[str]:
        """Get all active sessions for a project"""
        try:
            session_key = self._get_session_key(project_id)
            sessions = await self._redis_client.smembers(session_key)
            return list(sessions)
            
        except Exception as e:
            logger.error(f"Failed to get project sessions: {e}")
            return []
    
    async def cleanup_expired_contexts(self):
        """Clean up expired contexts (maintenance task)"""
        try:
            # This would typically be run as a background task
            # For now, we rely on Redis TTL for cleanup
            logger.info("Context cleanup completed (relying on Redis TTL)")
            
        except Exception as e:
            logger.error(f"Failed to cleanup contexts: {e}")
    
    async def get_context_stats(self, project_id: str) -> Dict[str, Any]:
        """Get context statistics for a project"""
        try:
            session_key = self._get_session_key(project_id)
            conversation_key = self._get_conversation_key(project_id)
            
            # Count sessions
            session_count = await self._redis_client.scard(session_key)
            
            # Count conversation messages
            conversation_count = await self._redis_client.llen(conversation_key)
            
            # Get sessions
            sessions = await self._redis_client.smembers(session_key)
            
            # Get context sizes
            context_sizes = {}
            for session_id in sessions:
                context_key = self._get_context_key(project_id, session_id)
                context_data = await self._redis_client.get(context_key)
                if context_data:
                    context_sizes[session_id] = len(context_data)
            
            return {
                "project_id": project_id,
                "active_sessions": session_count,
                "conversation_messages": conversation_count,
                "context_sizes": context_sizes,
                "total_memory_usage": sum(context_sizes.values())
            }
            
        except Exception as e:
            logger.error(f"Failed to get context stats: {e}")
            return {"error": str(e)}

# Global context manager instance
context_manager = ContextManager()