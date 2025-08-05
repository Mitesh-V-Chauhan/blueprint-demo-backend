from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import json

# Enums
class ProjectType(str, Enum):
    NEW_IDEA = "NEW_IDEA"
    REPO_ANALYSIS = "REPO_ANALYSIS"
    UPLOADED_PROJECT = "UPLOADED_PROJECT"

class Plan(str, Enum):
    STARTER = "STARTER"
    PRO = "PRO"
    TEAM = "TEAM"

class NodeType(str, Enum):
    FOLDER = "FOLDER"
    FILE = "FILE"

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class AgentType(str, Enum):
    SUPERVISOR = "supervisor"
    REQUIREMENTS = "requirements"
    ARCHITECT = "architect"
    DESIGNER = "designer"
    WRITER = "writer"
    CODE_GENERATOR = "code_generator"
    ANALYZER = "analyzer"

# Base Models
class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# User Models
class UserProfile(BaseModel):
    name: str = Field(default="Default User", description="User's name")
    role: Optional[str] = None
    experience_level: Optional[str] = None
    primary_goal: Optional[str] = None
    biggest_challenge: Optional[str] = None
    project_context: Optional[str] = None
    company_size: Optional[str] = None
    team_size: Optional[int] = None
    favorite_tech_stack: Optional[List[str]] = None
    current_project_tools: Optional[List[str]] = None
    project_types: Optional[List[str]] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)

class UserCreate(BaseModel):
    id: str  # Firebase UID
    email: str
    username: Optional[str] = None
    profile: Optional[UserProfile] = None

class UserResponse(TimestampMixin):
    id: str
    email: str
    username: Optional[str]
    plan: Plan
    project_count_this_month: int
    repo_analysis_count_this_month: int

# Project Models
class ProjectCreate(BaseModel):
    name: str
    user_input: str = Field(..., min_length=10, description="Initial project description")
    type: ProjectType = ProjectType.NEW_IDEA
    repo_url: Optional[str] = None
    team_id: Optional[str] = None

class ProjectResponse(TimestampMixin):
    id: str
    name: str
    user_input: str
    type: ProjectType
    repo_url: Optional[str]
    user_id: str
    team_id: Optional[str]

# Blueprint Generation Models
class BlueprintRequest(BaseModel):
    initial_idea: str = Field(..., min_length=10, description="The initial project idea")
    user_profile: UserProfile = Field(default_factory=UserProfile)
    user_answers: List[str] = Field(default_factory=list, description="Answers to clarifying questions")
    project_type: ProjectType = ProjectType.NEW_IDEA
    repo_url: Optional[str] = None

class ClarifyingQuestion(BaseModel):
    question: str
    context: Optional[str] = None

class TechStack(BaseModel):
    frontend: str
    backend: str
    database: str
    deployment: str
    additional_tools: List[str] = Field(default_factory=list)

class TechStackRecommendation(BaseModel):
    stack: TechStack
    justification: str
    alternatives: Dict[str, List[str]] = Field(default_factory=dict)
    reasoning: str

# Flowchart Models
class FlowchartNode(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]
    style: Optional[Dict[str, Any]] = None

class FlowchartEdge(BaseModel):
    id: str
    source: str
    target: str
    type: Optional[str] = "default"
    animated: Optional[bool] = False
    style: Optional[Dict[str, Any]] = None
    label: Optional[str] = None

class FlowchartData(BaseModel):
    nodes: List[FlowchartNode]
    edges: List[FlowchartEdge]

class FlowchartStateCreate(BaseModel):
    flowchart_json: FlowchartData
    change_description: Optional[str] = None
    project_id: str

class FlowchartStateResponse(TimestampMixin):
    id: str
    flowchart_json: FlowchartData
    change_description: Optional[str]
    project_id: str

# File Models
class FileNodeCreate(BaseModel):
    name: str
    path: str
    type: NodeType
    generated_code: Optional[str] = None
    explanation: Optional[str] = None
    project_id: str
    parent_id: Optional[str] = None

class FileNodeResponse(TimestampMixin):
    id: str
    name: str
    path: str
    type: NodeType
    generated_code: Optional[str]
    explanation: Optional[str]
    project_id: str
    parent_id: Optional[str]
    children: Optional[List['FileNodeResponse']] = None

class UploadedFileCreate(BaseModel):
    path: str
    content: str
    project_id: str

class UploadedFileResponse(TimestampMixin):
    id: str
    path: str
    content: str
    project_id: str

# Project Overview Models
class ProjectOverviewCreate(BaseModel):
    content: str
    user_flow: str
    tech_stack: Dict[str, Any]
    project_id: str

class ProjectOverviewResponse(TimestampMixin):
    id: str
    content: str
    user_flow: str
    tech_stack: Dict[str, Any]
    project_id: str

# Message Models
class MessageCreate(BaseModel):
    content: str
    role: Role
    project_id: str

class MessageResponse(TimestampMixin):
    id: str
    content: str
    role: Role
    project_id: str

# Agent Models
class AgentContext(BaseModel):
    project_id: str
    user_id: str
    session_id: str
    current_step: str
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    project_data: Dict[str, Any] = Field(default_factory=dict)
    rag_context: List[str] = Field(default_factory=list)

class AgentRequest(BaseModel):
    message: str
    agent_type: AgentType
    context: AgentContext
    tools_available: List[str] = Field(default_factory=list)

class AgentResponse(BaseModel):
    agent_type: AgentType
    message: str
    action_taken: Optional[str] = None
    updated_context: AgentContext
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

# Chat Models
class ChatRequest(BaseModel):
    message: str
    project_id: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    agent_type: AgentType
    actions_taken: List[str] = Field(default_factory=list)
    updated_components: List[str] = Field(default_factory=list)
    conversation_id: str

# Stream Models
class StreamChunk(BaseModel):
    type: str  # "message", "action", "complete", "error"
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

# Analysis Models
class CodeAnalysisResult(BaseModel):
    file_path: str
    language: str
    complexity_score: float
    patterns_detected: List[str]
    dependencies: List[str]
    suggestions: List[str]

class ProjectAnalysisResult(BaseModel):
    overview: str
    architecture_summary: str
    tech_stack_detected: TechStack
    file_structure: List[FileNodeResponse]
    code_analysis: List[CodeAnalysisResult]
    recommendations: List[str]

# Error Models
class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    error_code: Optional[str] = None

# Update forward references
FileNodeResponse.model_rebuild()