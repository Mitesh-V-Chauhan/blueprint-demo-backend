from agents.base_agent import BaseAgent
from models.schemas import AgentType, AgentContext
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
import json

class CodeGeneratorAgent(BaseAgent):
    def __init__(self, api_key_index: int = 6):
        super().__init__(AgentType.CODE_GENERATOR, api_key_index)
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [{"name": "generate_code", "description": "Generate project code files"}]
    
    def _get_system_prompt(self) -> str:
        return """You are a code generator. Create complete, production-ready code files based on:
        1. Tech stack specifications
        2. Architecture patterns
        3. Project requirements
        
        Generate 4-6 key files with explanations.
        Response with JSON: {"files": [{"fileName": "...", "code": "...", "explanation": "..."}]}"""
    
    async def _process_request(self, context: AgentContext) -> Dict[str, Any]:
        try:
            tech_stack = context.project_data.get("tech_stack", {})
            full_context = context.project_data.get("full_context", "")
            
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=f"Context: {full_context}\nTech Stack: {json.dumps(tech_stack)}")
            ]
            
            response = await self._invoke_llm(messages)
            result = self._extract_json_from_response(response)
            
            files = result.get("files", [])
            if not files:
                files = self._generate_fallback_files(tech_stack)
            
            return {
                "message": f"Generated {len(files)} code files",
                "action_taken": "code_generation",
                "files": files
            }
        except Exception as e:
            return {"message": f"Error: {e}", "action_taken": "error"}
    
    def _generate_fallback_files(self, tech_stack: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate basic fallback files"""
        frontend = tech_stack.get("frontend", {})
        backend = tech_stack.get("backend", {})
        
        files = []
        
        if frontend.get("framework") == "React":
            files.append({
                "fileName": "src/App.tsx",
                "code": "import React from 'react';\n\nfunction App() {\n  return <div>Hello World</div>;\n}\n\nexport default App;",
                "explanation": "Main React application component"
            })
        
        if backend.get("framework") == "FastAPI":
            files.append({
                "fileName": "main.py",
                "code": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}",
                "explanation": "FastAPI main application file"
            })
        
        return files