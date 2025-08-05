import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
import json
import asyncio
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from utils.config import Settings
from models.schemas import AgentContext, AgentResponse, AgentType
from context.context_manager import ContextManager
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_type: AgentType, api_key_index: int = 1):
        self.agent_type = agent_type
        self.settings = Settings()
        self.api_key_index = api_key_index
        self.context_manager = ContextManager()
        self.vector_store = VectorStore()
        
        # Initialize LLM
        self._initialize_llm()
        
        # Agent-specific tools
        self.tools = self._get_tools()
        
        logger.info(f"Initialized {self.agent_type} agent")
    
    def _initialize_llm(self):
        """Initialize the language model"""
        try:
            api_keys = self.settings.gemini_api_keys
            if not api_keys:
                raise ValueError("No Gemini API keys available")
            
            # Use modulo to cycle through available keys
            key_index = (self.api_key_index - 1) % len(api_keys)
            api_key = api_keys[key_index]
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.1,
                max_tokens=8192,
                timeout=120,
                max_retries=2
            )
            
            logger.info(f"Initialized LLM for {self.agent_type} with API key index {key_index}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM for {self.agent_type}: {e}")
            raise
    
    @abstractmethod
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Get agent-specific tools"""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get agent-specific system prompt"""
        pass
    
    @abstractmethod
    async def _process_request(self, context: AgentContext) -> Dict[str, Any]:
        """Process the main request logic"""
        pass
    
    async def execute(self, context: AgentContext) -> AgentResponse:
        """Execute the agent's main logic"""
        try:
            logger.info(f"Executing {self.agent_type} agent for project {context.project_id}")
            
            # Update context with agent information
            context.current_step = self.agent_type.value
            
            # Get relevant context from RAG
            rag_context = await self._get_rag_context(context)
            context.rag_context = rag_context
            
            # Process the request
            result = await self._process_request(context)
            
            # Update context with results
            context.project_data.update(result)
            
            # Save context
            await self.context_manager.save_context(context)
            
            # Determine confidence score
            confidence = self._calculate_confidence(result)
            
            return AgentResponse(
                agent_type=self.agent_type,
                message=result.get('message', 'Task completed successfully'),
                action_taken=result.get('action_taken'),
                updated_context=context,
                tool_calls=result.get('tool_calls', []),
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error executing {self.agent_type} agent: {e}")
            
            # Return error response
            return AgentResponse(
                agent_type=self.agent_type,
                message=f"Error: {str(e)}",
                updated_context=context,
                confidence=0.0
            )
    
    async def _get_rag_context(self, context: AgentContext) -> List[str]:
        """Get relevant context from vector store"""
        try:
            if not context.conversation_history:
                return []
            
            # Get the last user message
            last_message = context.conversation_history[-1].get('content', '')
            
            # Search for relevant documents
            search_results = await self.vector_store.search_project_knowledge(
                project_id=context.project_id,
                query=last_message,
                limit=3
            )
            
            # Extract relevant content
            rag_context = []
            for result in search_results:
                if result['score'] > 0.7:  # Only include highly relevant results
                    rag_context.append(result['content'][:500])  # Truncate to manage tokens
            
            return rag_context
            
        except Exception as e:
            logger.error(f"Error getting RAG context: {e}")
            return []
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score for the result"""
        try:
            # Base confidence factors
            factors = []
            
            # Check if result has expected fields
            if 'message' in result and result['message']:
                factors.append(0.3)
            
            if 'action_taken' in result and result['action_taken']:
                factors.append(0.2)
            
            # Check if any errors occurred
            if 'error' not in result:
                factors.append(0.3)
            
            # Check result completeness
            if len(str(result.get('message', ''))) > 50:
                factors.append(0.2)
            
            return min(sum(factors), 1.0)
            
        except Exception:
            return 0.5  # Default moderate confidence
    
    async def _invoke_llm(self, messages: List[BaseMessage]) -> str:
        """Invoke the language model with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.llm.ainvoke(messages)
                return response.content
            except Exception as e:
                logger.warning(f"LLM invocation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find any JSON object
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return {}
        except json.JSONDecodeError:
            logger.warning("Failed to extract JSON from LLM response")
            return {}
    
    def _build_context_prompt(self, context: AgentContext) -> str:
        """Build context prompt from agent context"""
        prompt_parts = []
        
        # Add project information
        if context.project_data:
            prompt_parts.append(f"Project Context: {json.dumps(context.project_data, indent=2)}")
        
        # Add conversation history
        if context.conversation_history:
            recent_history = context.conversation_history[-5:]  # Last 5 messages
            history_text = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in recent_history
            ])
            prompt_parts.append(f"Recent Conversation:\n{history_text}")
        
        # Add RAG context
        if context.rag_context:
            rag_text = "\n\n".join(context.rag_context)
            prompt_parts.append(f"Relevant Context:\n{rag_text}")
        
        return "\n\n".join(prompt_parts)

class AgentExecutor:
    """Manages the execution of multiple agents"""
    
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.context_manager = ContextManager()
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.agent_type] = agent
        logger.info(f"Registered {agent.agent_type} agent")
    
    async def execute_agent(self, agent_type: AgentType, context: AgentContext) -> AgentResponse:
        """Execute a specific agent"""
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type} not registered")
        
        agent = self.agents[agent_type]
        return await agent.execute(context)
    
    async def execute_workflow(self, workflow_steps: List[AgentType], 
                             initial_context: AgentContext) -> List[AgentResponse]:
        """Execute a workflow of agents"""
        responses = []
        current_context = initial_context
        
        for agent_type in workflow_steps:
            try:
                response = await self.execute_agent(agent_type, current_context)
                responses.append(response)
                
                # Update context for next agent
                current_context = response.updated_context
                
                # Stop on error
                if response.confidence < 0.3:
                    logger.warning(f"Low confidence response from {agent_type}, stopping workflow")
                    break
                    
            except Exception as e:
                logger.error(f"Error in workflow at {agent_type}: {e}")
                break
        
        return responses