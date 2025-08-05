from agents.base_agent import BaseAgent
from models.schemas import AgentType, AgentContext
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
import json

class WriterAgent(BaseAgent):
    def __init__(self, api_key_index: int = 5):
        super().__init__(AgentType.WRITER, api_key_index)
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [{"name": "write_documentation", "description": "Generate project documentation"}]
    
    def _get_system_prompt(self) -> str:
        return """You are a technical writer. Create comprehensive project documentation including:
        1. Project overview and goals
        2. User flow descriptions
        3. Technical specifications
        4. Setup and deployment guides
        
        Response with JSON: {"project_overview": "...", "user_flow": "...", "technical_specs": "..."}"""
    
    async def _process_request(self, context: AgentContext) -> Dict[str, Any]:
        try:
            full_context = context.project_data.get("full_context", "")
            tech_stack = context.project_data.get("tech_stack", {})
            
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=f"Context: {full_context}\nTech Stack: {json.dumps(tech_stack)}")
            ]
            
            response = await self._invoke_llm(messages)
            result = self._extract_json_from_response(response)
            
            return {
                "message": "Documentation generated successfully",
                "action_taken": "documentation_generation",
                "project_overview": result.get("project_overview", ""),
                "user_flow": result.get("user_flow", ""),
                "technical_specs": result.get("technical_specs", "")
            }
        except Exception as e:
            return {"message": f"Error: {e}", "action_taken": "error"}