import os
import json
import asyncio
import re
import ast
from typing import List, Dict, Any, TypedDict, Optional
import logging
from datetime import datetime
import uuid

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# ==============================================================================
# 1. LOGGING CONFIGURATION
# ==============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==============================================================================
# 2. INITIAL SETUP & CONFIGURATION
# ==============================================================================
load_dotenv()

# --- Pydantic Models ---
class UserProfile(BaseModel):
    name: str = Field(default="Default User", description="User's name")
    experience: str = Field(default="Intermediate", description="Programming experience level")

class BlueprintRequest(BaseModel):
    initial_idea: str = Field(..., min_length=10, description="The initial project idea")
    user_profile: UserProfile = Field(default_factory=UserProfile)
    user_answers: List[str] = Field(default_factory=list, description="Answers to clarifying questions")

class QuestionRequest(BaseModel):
    initial_idea: str = Field(..., min_length=10, description="The initial project idea")
    user_profile: UserProfile = Field(default_factory=UserProfile)

# --- Agent State Definition ---
class AgentState(TypedDict):
    initial_idea: str
    user_profile: Dict[str, Any]
    user_answers: List[str]
    full_context: str
    clarifying_questions: List[str]
    tech_stack: Dict[str, Any]
    flowchart: Dict[str, Any]
    files: List[Dict[str, str]]
    processing_status: str
    error_count: int
    project_structure: Dict[str, Any]
    documentation: Dict[str, Any]

# ==============================================================================
# 3. ENHANCED LLM SERVICE (WITH MULTI-API-KEY SUPPORT)
# ==============================================================================
class LLMService:
    _model_cache = {}
    _api_keys = []
    _key_assignments = {
        'requirements': 'GEMINI_API_KEY_1',
        'architect': 'GEMINI_API_KEY_2',
        'designer': 'GEMINI_API_KEY_3',
        'structure_docs': 'GEMINI_API_KEY_4',
        'documentation': 'GEMINI_API_KEY_6',  # Separate key for documentation
        'code_generator': 'GEMINI_API_KEY_5',
        'fallback': 'GEMINI_API_KEY_1'  # Fallback to first key
    }

    @classmethod
    def _initialize_api_keys(cls):
        """Initialize and validate all available API keys"""
        if not cls._api_keys:  # Only initialize once
            available_keys = []
            for i in range(1, 7):  # Check GEMINI_API_KEY_1 through GEMINI_API_KEY_6
                key = os.getenv(f"GEMINI_API_KEY_{i}")
                if key and key.strip():  # Check key exists and is not empty
                    # Basic validation - Gemini API keys should start with certain patterns
                    if len(key.strip()) > 10:  # Basic length check
                        available_keys.append((f"GEMINI_API_KEY_{i}", key.strip()))
                        logger.info(f"✅ Found valid API key: GEMINI_API_KEY_{i} (length: {len(key.strip())})")
                    else:
                        logger.error(f"❌ Invalid API key format: GEMINI_API_KEY_{i} (too short: {len(key.strip())} chars)")
                else:
                    logger.warning(f"⚠️  API key not found or empty: GEMINI_API_KEY_{i}")

            if not available_keys:
                logger.error("❌ No valid GEMINI API keys found!")
                logger.error("Please check your .env file and ensure you have valid API keys set.")
                logger.error("Example: GEMINI_API_KEY_1=AIzaSyC9XR7...")
                raise ValueError("No valid GEMINI API keys found. Please set GEMINI_API_KEY_1 through GEMINI_API_KEY_6 in .env file")

            cls._api_keys = available_keys
            logger.info(f"🎉 Successfully initialized {len(available_keys)} valid API keys")

            # Show which agents will use which keys
            for agent_type, key_name in cls._key_assignments.items():
                found_key = any(k[0] == key_name for k in available_keys)
                if found_key:
                    logger.info(f"🔑 {agent_type.upper()} agent → {key_name} ✅")
                else:
                    logger.warning(f"⚠️  {agent_type.upper()} agent → {key_name} (will use fallback)")

    @classmethod
    def get_model(cls, agent_type: str = 'fallback') -> ChatGoogleGenerativeAI:
        """Get a model instance for a specific agent type with dedicated API key"""
        cls._initialize_api_keys()

        # Get the assigned API key for this agent type
        key_name = cls._key_assignments.get(agent_type, 'GEMINI_API_KEY_6')

        # Find the actual API key value
        api_key = None
        for key_env_name, key_value in cls._api_keys:
            if key_env_name == key_name:
                api_key = key_value
                break

        # Fallback to any available key if assigned key not found
        if not api_key:
            logger.warning(f"Assigned key {key_name} not found for {agent_type}, using fallback")
            api_key = cls._api_keys[0][1]  # Use first available key
            key_name = cls._api_keys[0][0]

        # Check cache for this specific key
        cache_key = f"{agent_type}_{key_name}"
        if cache_key in cls._model_cache:
            return cls._model_cache[cache_key]

        try:
            logger.info(f"🔄 Initializing Gemini model for {agent_type} using {key_name}")
            model = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.1,
                timeout=120,
                max_retries=2
            )
            cls._model_cache[cache_key] = model
            logger.info(f"✅ Successfully initialized Gemini model for {agent_type} using {key_name}")
            return model
        except Exception as e:
            logger.error(f"❌ Failed to initialize model for {agent_type} with {key_name}")
            logger.error(f"   Error details: {str(e)}")

            # Check if it's an API key error
            if "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
                logger.error(f"   🔑 INVALID API KEY: {key_name}")
                logger.error(f"   Please check that {key_name} is set correctly in your .env file")
                logger.error(f"   Current key length: {len(api_key)} characters")
                logger.error(f"   Key starts with: {api_key[:10]}...")

            # Try fallback with a different key
            if len(cls._api_keys) > 1:
                # Try all available keys as fallback
                for fallback_name, fallback_key in cls._api_keys:
                    if fallback_name != key_name:  # Don't retry the same key
                        logger.warning(f"🔄 Trying fallback key {fallback_name} for {agent_type}")
                        try:
                            model = ChatGoogleGenerativeAI(
                                model="gemini-1.5-flash",
                                google_api_key=fallback_key,
                                temperature=0.1,
                                timeout=120,
                                max_retries=2
                            )
                            cls._model_cache[f"{agent_type}_fallback_{fallback_name}"] = model
                            logger.info(f"✅ Successfully initialized fallback model for {agent_type} using {fallback_name}")
                            return model
                        except Exception as fallback_error:
                            logger.error(f"❌ Fallback {fallback_name} also failed for {agent_type}: {fallback_error}")
                            continue

            logger.error(f"💥 ALL API KEYS FAILED for {agent_type}. Please check your API keys!")
            raise

    @staticmethod
    def parse_llm_json_output(text: str) -> Any:
        """
        UPDATED: This parser now handles both JSON objects AND arrays,
        and is more resilient to extraction failures.
        """
        # Regex to find JSON object or array within markdown fences
        match = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', text, re.DOTALL)

        if match:
            json_string = match.group(1)
        else:
            # Fallback for responses without markdown fences
            # Find the first '{' or '[' and the last '}' or ']'
            start_bracket = text.find('[')
            start_brace = text.find('{')

            if start_brace == -1 and start_bracket == -1:
                 logger.error(f"Could not find a JSON object or array in the LLM response: {text}")
                 return {"error": "No JSON object or array found in response"}

            start_index = -1
            if start_brace != -1 and start_bracket != -1:
                start_index = min(start_brace, start_bracket)
            elif start_brace != -1:
                start_index = start_brace
            else:
                start_index = start_bracket

            end_index = text.rfind('}') if text[start_index] == '{' else text.rfind(']')
            if end_index == -1:
                 logger.error(f"Could not find a matching closing bracket/brace in LLM response: {text}")
                 return {"error": "Mismatched brackets in response"}

            json_string = text[start_index : end_index + 1]

        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            logger.warning("Standard JSON parsing failed. Attempting to parse as Python literal.")
            try:
                return ast.literal_eval(json_string)
            except (SyntaxError, ValueError) as e:
                logger.error(f"Fatal parsing error. Could not parse as JSON or Python literal: {e}")
                logger.error(f"--- Malformed String ---:\n{json_string}\n--------------------")
                return {"error": "Failed to parse malformed response from AI model.", "details": json_string}

# ==============================================================================
# 4. BLUEPRINT GENERATOR LOGIC
# ==============================================================================
class BlueprintGenerator:

    @staticmethod
    async def generate_clarifying_questions(initial_idea: str, user_profile: dict) -> List[str]:
        model = LLMService.get_model('requirements')  # Use dedicated API key for requirements
        prompt = f"""
        You are an expert requirements analyst. Based on this project idea: "{initial_idea}"
        and user profile: {json.dumps(user_profile)}, generate exactly 3 concise, specific clarifying questions.
        Focus on: core functionality, target audience, and technical constraints.
        Respond with ONLY a valid JSON array of strings. Example:
        ["What are the main features?", "Who is the target audience?", "Any preferred technologies?"]
        """
        response = await model.ainvoke(prompt)

        # FIXED: Use the robust universal parser here as well.
        questions = LLMService.parse_llm_json_output(response.content)

        if isinstance(questions, list) and len(questions) > 0:
            return questions
        else:
            logger.warning(f"Failed to parse questions or got non-list/empty list. Using fallback. Got: {questions}")
            return [
                "What are the core features you envision for this application?",
                "Who is the primary target audience for this project?",
                "Are there any specific technologies or platforms you must use?"
            ]

    # --- Other generator functions now just call the robust parser ---
    @staticmethod
    async def generate_tech_stack(full_context: str) -> Dict[str, Any]:
        model = LLMService.get_model('architect')  # Use dedicated API key for architect
        prompt = f"""
        You are a technical architect. Based on the project context: "{full_context}"

        Generate a comprehensive tech stack recommendation that includes:
        - Frontend technologies
        - Backend technologies
        - Database recommendations
        - Deployment platform
        - Development tools

        Respond with ONLY a valid JSON object in this format:
        {{
            "frontend": {{"framework": "React", "styling": "Tailwind CSS", "language": "TypeScript"}},
            "backend": {{"framework": "FastAPI", "language": "Python", "runtime": "Python 3.9+"}},
            "database": {{"primary": "PostgreSQL", "cache": "Redis"}},
            "deployment": {{"platform": "Vercel", "containerization": "Docker"}},
            "tools": {{"version_control": "Git", "package_manager": "npm", "bundler": "Vite"}}
        }}
        """
        response = await model.ainvoke(prompt)
        return LLMService.parse_llm_json_output(response.content)

    @staticmethod
    async def generate_comprehensive_flowchart(full_context: str, tech_stack: dict) -> Dict[str, Any]:
        model = LLMService.get_model('designer')  # Use dedicated API key for designer
        prompt = f"""
        You are a system designer. Based on the project context: "{full_context}"
        and tech stack: {json.dumps(tech_stack)}

        Create a comprehensive application flowchart that shows:
        - User interactions and flows
        - System components and their relationships
        - Data flow between components
        - External integrations

        Respond with ONLY a valid JSON object in this format (nodes must have position coordinates):
        {{
            "title": "Application Flow Diagram",
            "nodes": [
                {{"id": "user", "position": {{"x": 100, "y": 50}}, "data": {{"label": "User", "type": "user"}}, "type": "ui"}},
                {{"id": "frontend", "position": {{"x": 300, "y": 50}}, "data": {{"label": "Frontend App", "type": "component"}}, "type": "ui"}},
                {{"id": "api", "position": {{"x": 500, "y": 50}}, "data": {{"label": "API Server", "type": "component"}}, "type": "logic"}},
                {{"id": "database", "position": {{"x": 700, "y": 50}}, "data": {{"label": "Database", "type": "storage"}}, "type": "data"}}
            ],
            "edges": [
                {{"id": "e1", "source": "user", "target": "frontend", "label": "interacts with"}},
                {{"id": "e2", "source": "frontend", "target": "api", "label": "API calls"}},
                {{"id": "e3", "source": "api", "target": "database", "label": "queries"}}
            ]
        }}
        """
        response = await model.ainvoke(prompt)
        return LLMService.parse_llm_json_output(response.content)

    @staticmethod
    async def generate_project_structure(full_context: str, tech_stack: dict) -> Dict[str, Any]:
        model = LLMService.get_model('structure_docs')  # Use dedicated API key for structure & docs
        prompt = f"""
        You are a project structure architect. Based on the project context: "{full_context}"
        and tech stack: {json.dumps(tech_stack)}

        Generate a comprehensive project folder structure that includes:
        - Root directory structure
        - Source code organization
        - Configuration files
        - Asset directories
        - Documentation structure

        Respond with ONLY a valid JSON object in this format:
        {{
            "name": "project-root",
            "type": "folder",
            "path": "/",
            "children": [
                {{
                    "name": "src",
                    "type": "folder",
                    "path": "/src",
                    "children": [
                        {{"name": "components", "type": "folder", "path": "/src/components"}},
                        {{"name": "pages", "type": "folder", "path": "/src/pages"}},
                        {{"name": "utils", "type": "folder", "path": "/src/utils"}}
                    ]
                }},
                {{"name": "package.json", "type": "file", "path": "/package.json"}},
                {{"name": "README.md", "type": "file", "path": "/README.md"}}
            ]
        }}
        """
        response = await model.ainvoke(prompt)
        return LLMService.parse_llm_json_output(response.content)

    @staticmethod
    async def generate_documentation(full_context: str, tech_stack: dict) -> Dict[str, Any]:
        model = LLMService.get_model('documentation')  # Use dedicated API key for documentation
        prompt = f"""
        You are a technical documentation specialist. Based on the project context: "{full_context}"
        and tech stack: {json.dumps(tech_stack)}

        Generate comprehensive project documentation that includes:
        - Project overview and description
        - Installation instructions
        - Usage guidelines
        - API documentation structure
        - Contributing guidelines

        Respond with ONLY a valid JSON object in this format:
        {{
            "readme": {{
                "title": "Project Name",
                "description": "Brief project description",
                "installation": ["npm install", "npm run dev"],
                "usage": "How to use the application",
                "features": ["Feature 1", "Feature 2"]
            }},
            "api_docs": {{
                "endpoints": [
                    {{"method": "GET", "path": "/api/users", "description": "Get all users"}},
                    {{"method": "POST", "path": "/api/users", "description": "Create user"}}
                ]
            }},
            "contributing": {{
                "guidelines": ["Fork the repository", "Create feature branch", "Submit pull request"],
                "code_style": "Follow ESLint configuration"
            }}
        }}
        """
        response = await model.ainvoke(prompt)
        return LLMService.parse_llm_json_output(response.content)

    @staticmethod
    async def generate_project_files(full_context: str, tech_stack: dict, structure: dict) -> List[Dict[str, str]]:
        def extract_all_files(node, files):
            if isinstance(node, dict):
                if node.get("type") == "file" and "path" in node:
                    files.append(node["path"])
                if "children" in node and isinstance(node["children"], list):
                    for child in node["children"]:
                        extract_all_files(child, files)

        def get_boilerplate_template(file_path: str, context: str, tech_stack: dict) -> str:
            """Generate boilerplate based on file type"""
            file_ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
            file_name = file_path.split('/')[-1]

            if file_ext == 'js' or file_ext == 'jsx':
                if 'react' in str(tech_stack).lower():
                    return f"""import React from 'react';

function {file_name.replace('.js', '').replace('.jsx', '').replace('-', '').replace('_', '')}() {{
  // TODO: Implement component logic
  return (
    <div>
      <h1>TODO: Implement {file_name}</h1>
    </div>
  );
}}

export default {file_name.replace('.js', '').replace('.jsx', '').replace('-', '').replace('_', '')};"""
                else:
                    return f"""// {file_name} - {context}

// TODO: Implement main functionality
function main() {{
  console.log('TODO: Implement {file_name}');
}}

// TODO: Add exports
module.exports = {{ main }};"""

            elif file_ext == 'ts' or file_ext == 'tsx':
                return f"""// {file_name} - TypeScript implementation

interface {file_name.replace('.ts', '').replace('.tsx', '')}Props {{
  // TODO: Define component props
}}

// TODO: Implement main functionality
export const {file_name.replace('.ts', '').replace('.tsx', '')} = () => {{
  // TODO: Add implementation
  return null;
}};"""

            elif file_ext == 'py':
                return f'''"""
{file_name} - {context}

TODO: Add module description
"""

def main():
    """TODO: Implement main functionality"""
    print("TODO: Implement {file_name}")

if __name__ == "__main__":
    main()'''

            elif file_ext == 'html':
                return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TODO: Add page title</title>
    </head>
<body>
    <h1>TODO: Implement {file_name}</h1>

    </body>
</html>"""

            elif file_ext == 'css':
                return f"""/* {file_name} - Stylesheet */

/* TODO: Add global styles */
* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

/* TODO: Add component styles */
.container {{
  /* TODO: Add container styles */
}}

/* TODO: Add responsive styles */
@media (max-width: 768px) {{
  /* TODO: Add mobile styles */
}}"""

            elif file_ext == 'json':
                if 'package.json' in file_name:
                    return """{
  "name": "project-name",
  "version": "1.0.0",
  "description": "TODO: Add project description",
  "main": "index.js",
  "scripts": {
    "start": "TODO: Add start script",
    "build": "TODO: Add build script",
    "test": "TODO: Add test script"
  },
  "dependencies": {
    "TODO": "Add dependencies"
  },
  "devDependencies": {
    "TODO": "Add dev dependencies"
  }
}"""
                else:
                    return """{
  "TODO": "Add configuration values"
}"""

            elif file_ext == 'md':
                return f"""# {file_name.replace('.md', '').replace('-', ' ').replace('_', ' ').title()}

TODO: Add description

## Installation

TODO: Add installation instructions

## Usage

TODO: Add usage instructions

## Features

TODO: List features

## Contributing

TODO: Add contributing guidelines"""

            elif file_ext in ['yml', 'yaml']:
                return f"""# {file_name} - Configuration file

# TODO: Add configuration
name: project-name
version: "1.0.0"

# TODO: Add more configuration options"""

            else:
                return f"""# {file_name}
# TODO: Implement {file_name}
# Context: {context}"""

        # Extract all files from structure
        all_file_paths = []
        try:
            extract_all_files(structure, all_file_paths)
        except Exception as e:
            logger.warning(f"Error extracting file paths from structure: {e}")

        # Filter for code files and important config files
        important_files = []
        for path in all_file_paths:
            if any(ext in path.lower() for ext in ['.js', '.jsx', '.ts', '.tsx', '.py', '.html', '.css', '.json', '.md', '.yml', '.yaml']):
                important_files.append(path)

        # If no files found, use comprehensive fallback
        if not important_files:
            logger.warning("No files found in structure, using comprehensive fallback")
            frontend = tech_stack.get('frontend', {})
            backend = tech_stack.get('backend', {})

            important_files = [
                "/package.json",
                "/README.md",
                "/src/index.js" if 'react' in str(frontend).lower() else "/src/main.py",
                "/src/App.js" if 'react' in str(frontend).lower() else "/src/app.py",
                "/src/components/Header.js" if 'react' in str(frontend).lower() else "/src/components.py",
                "/src/styles/main.css",
                "/public/index.html" if 'react' in str(frontend).lower() else "/templates/index.html"
            ]

        logger.info(f"Generating code for {len(important_files)} files: {important_files}")

        model = LLMService.get_model('code_generator')  # Use dedicated API key for code generation
        all_files = []

        # Process each file with appropriate boilerplate
        for file_path in important_files:
            try:
                # First try to get template-based boilerplate
                boilerplate_code = get_boilerplate_template(file_path, full_context, tech_stack)

                # For complex files, enhance with LLM
                if any(ext in file_path for ext in ['.js', '.jsx', '.ts', '.tsx', '.py']) and len(boilerplate_code) < 200:
                    enhanced_prompt = f"""
                    Enhance this boilerplate code for {file_path}:
                    {boilerplate_code}

                    Project Context: {full_context}
                    Tech Stack: {json.dumps(tech_stack)}

                    Add more detailed boilerplate structure but keep TODO comments for main logic.
                    Return ONLY the enhanced code, no explanations.
                    """
                    try:
                        response = await model.ainvoke(enhanced_prompt)
                        enhanced_code = response.content.strip()
                        # Clean up any markdown formatting
                        for lang in ['```typescript', '```javascript', '```python', '```jsx', '```tsx', '```']:
                            enhanced_code = enhanced_code.replace(lang, '')
                        enhanced_code = enhanced_code.replace('```', '')

                        if len(enhanced_code.strip()) > 50:  # Use enhanced version if substantial
                            boilerplate_code = enhanced_code.strip()
                    except Exception as e:
                        logger.warning(f"Failed to enhance {file_path}, using template: {e}")

                all_files.append({
                    "fileName": file_path,
                    "code": boilerplate_code,
                    "explanation": f"Boilerplate code for {file_path.split('/')[-1]}"
                })
                logger.info(f"Generated boilerplate for {file_path}")

            except Exception as e:
                logger.error(f"Error generating {file_path}: {e}")
                all_files.append({
                    "fileName": file_path,
                    "code": f"# Error generating {file_path}: {str(e)}",
                    "explanation": f"Error occurred while generating {file_path}"
                })

        logger.info(f"Code generation completed with {len(all_files)} files")
        return all_files


# ==============================================================================
# 5. AGENT GRAPH DEFINITION (CORRECTED)
# ==============================================================================
def create_agent_graph():
    """
    Creates the agent graph with the corrected logical flow.
    The question generation part is handled by a separate endpoint,
    so this graph starts directly with the architect.
    """
    async def architect_node(state: AgentState):
        logger.info("--- Running Architect ---")
        tech_stack = await BlueprintGenerator.generate_tech_stack(state["full_context"])
        return {"tech_stack": tech_stack}

    async def designer_node(state: AgentState):
        logger.info("--- Running Designer (Flowchart) ---")
        flowchart = await BlueprintGenerator.generate_comprehensive_flowchart(state["full_context"], state["tech_stack"])
        return {"flowchart": flowchart}

    async def structure_and_docs_node(state: AgentState):
        logger.info("--- Running Structure & Docs Generator ---")
        structure, documentation = await asyncio.gather(
            BlueprintGenerator.generate_project_structure(state["full_context"], state["tech_stack"]),
            BlueprintGenerator.generate_documentation(state["full_context"], state["tech_stack"])
        )
        return {"project_structure": structure, "documentation": documentation}

    async def coder_node(state: AgentState):
        logger.info("--- Running Code Generator ---")
        try:
            files = await BlueprintGenerator.generate_project_files(state["full_context"], state["tech_stack"], state["project_structure"])
            logger.info(f"Code Generator completed with {len(files)} files")
            return {"files": files}
        except Exception as e:
            logger.error(f"Code Generator failed: {e}")
            return {"files": [{"fileName": "error.txt", "code": f"Error: {str(e)}", "explanation": "Code generation failed"}]}

    workflow = StateGraph(AgentState)

    # Add the nodes that are part of the blueprint generation flow
    workflow.add_node("Architect", architect_node)
    workflow.add_node("Designer", designer_node)
    workflow.add_node("Structure_and_Docs_Generator", structure_and_docs_node)
    workflow.add_node("Code_Generator", coder_node)

    # ** THE FIX **
    # The graph now correctly starts at the 'Architect' node, as the
    # requirements-gathering phase is completed before this graph is invoked.
    workflow.set_entry_point("Architect")

    # Define the clear, linear sequence of the workflow
    workflow.add_edge("Architect", "Designer")
    workflow.add_edge("Designer", "Structure_and_Docs_Generator")
    workflow.add_edge("Structure_and_Docs_Generator", "Code_Generator")
    workflow.add_edge("Code_Generator", END)

    return workflow.compile()


# ==============================================================================
# 6. FASTAPI APPLICATION
# ==============================================================================
app = FastAPI(title="AI Blueprint Generator API", version="3.4.0") # Version bump for fix
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
agent_graph = create_agent_graph()

@app.get("/")
async def root():
    return {"status": "API is running"}

@app.post("/api/v1/generate-questions")
async def generate_questions(request: QuestionRequest):
    try:
        # This endpoint correctly calls the static method directly. It does not use the graph.
        questions = await BlueprintGenerator.generate_clarifying_questions(request.initial_idea, request.user_profile.dict())
        return {"questions": questions}
    except Exception as e:
        logger.error(f"Error in /generate-questions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate-blueprint")
async def generate_blueprint(request: BlueprintRequest):
    initial_state = {
        "initial_idea": request.initial_idea,
        "user_profile": request.user_profile.dict(),
        "user_answers": request.user_answers,
        "full_context": f"Project Idea: {request.initial_idea}\nUser Profile: {request.user_profile.name} ({request.user_profile.experience})\nClarifications:\n" + "\n".join(request.user_answers),
    }

    async def stream_generator():
        final_state = {}
        node_count = 0
        expected_nodes = ['Architect', 'Designer', 'Structure_and_Docs_Generator', 'Code_Generator']
        
        try:
            async for chunk in agent_graph.astream(initial_state, {"recursion_limit": 15}):
                node_name = list(chunk.keys())[0]
                logger.info(f"Processing chunk from: {node_name}")
                logger.info(f"Chunk keys: {list(chunk.keys())}")
                logger.info(f"Chunk data: {chunk}")

                if node_name != "__end__":
                    node_count += 1
                    if chunk[node_name]:
                        final_state.update(chunk[node_name])
                    yield f"data: {json.dumps({'agent': node_name, 'output': chunk[node_name]})}\n\n"
                    await asyncio.sleep(0.1)
                else:
                    logger.info("🎉 Reached __end__ node, preparing completion payload.")
                    logger.info(f"Final state keys: {list(final_state.keys())}")
                    break  # Exit the loop to handle completion outside
            
            # Handle completion outside the loop (in case __end__ node is not streamed)
            logger.info(f"📊 Processed {node_count} nodes. Expected: {len(expected_nodes)}")
            
            # Always send completion payload after loop ends
            completion_payload = {
                'agent': 'COMPLETE',
                'output': {
                    'project': {
                        'id': str(uuid.uuid4()),
                        'name': ' '.join(request.initial_idea.split(' ', 3)[:3]) + ' Project',
                        'description': request.initial_idea,
                        'fileStructure': [final_state.get('project_structure', {})],
                        'documentation': final_state.get('documentation', {}),
                        'codeFiles': {file['fileName']: file['code'] for file in final_state.get('files', []) if 'fileName' in file},
                        'files': final_state.get('files', [])
                    },
                    'flowchart': final_state.get('flowchart', {}),
                },
                'timestamp': datetime.now().isoformat()
            }
            logger.info(f"🚀 Sending completion payload with {len(final_state.get('files', []))} files")
            yield f"data: {json.dumps(completion_payload)}\n\n"
            logger.info("✅ Completion payload sent successfully")
            logger.info("📄 Stream loop completed successfully")
        except Exception as e:
            logger.error(f"Stream generation error: {e}", exc_info=True)
            error_payload = {"agent": "ERROR", "output": {"error": "Blueprint generation failed", "details": str(e)}}
            yield f"data: {json.dumps(error_payload)}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )