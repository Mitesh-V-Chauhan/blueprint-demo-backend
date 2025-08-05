import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncpg
import json
from contextlib import asynccontextmanager

from utils.config import Settings
from models.schemas import (
    ProjectCreate, ProjectResponse, UserCreate, UserResponse,
    ProjectOverviewCreate, ProjectOverviewResponse,
    FlowchartStateCreate, FlowchartStateResponse,
    FileNodeCreate, FileNodeResponse,
    UploadedFileCreate, UploadedFileResponse,
    MessageCreate, MessageResponse,
    ProjectType, Plan, NodeType, Role
)

logger = logging.getLogger(__name__)

class Database:
    _pool: Optional[asyncpg.Pool] = None
    _settings: Settings = Settings()
    
    @classmethod
    async def initialize(cls):
        """Initialize database connection pool"""
        try:
            cls._pool = await asyncpg.create_pool(
                cls._settings.DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @classmethod
    async def close(cls):
        """Close database connection pool"""
        if cls._pool:
            await cls._pool.close()
            logger.info("Database connection pool closed")
    
    @classmethod
    async def health_check(cls) -> str:
        """Check database health"""
        try:
            async with cls._pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return f"unhealthy: {e}"
    
    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """Get database connection from pool"""
        async with cls._pool.acquire() as conn:
            yield conn

    # User operations
    @classmethod
    async def create_user(cls, user: UserCreate) -> UserResponse:
        """Create a new user"""
        async with cls.get_connection() as conn:
            query = """
                INSERT INTO "User" (id, email, username, "createdAt", "updatedAt")
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """
            now = datetime.now()
            row = await conn.fetchrow(
                query, user.id, user.email, user.username, now, now
            )
            return cls._row_to_user_response(row)
    
    @classmethod
    async def get_user(cls, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        async with cls.get_connection() as conn:
            query = 'SELECT * FROM "User" WHERE id = $1'
            row = await conn.fetchrow(query, user_id)
            return cls._row_to_user_response(row) if row else None
    
    @classmethod
    async def update_user_usage(cls, user_id: str, project_count: int = 0, repo_count: int = 0):
        """Update user usage counters"""
        async with cls.get_connection() as conn:
            query = """
                UPDATE "User" 
                SET "projectCountThisMonth" = "projectCountThisMonth" + $2,
                    "repoAnalysisCountThisMonth" = "repoAnalysisCountThisMonth" + $3,
                    "updatedAt" = $4
                WHERE id = $1
            """
            await conn.execute(query, user_id, project_count, repo_count, datetime.now())

    # Project operations
    @classmethod
    async def create_project(cls, project: ProjectCreate, user_id: str) -> ProjectResponse:
        """Create a new project"""
        async with cls.get_connection() as conn:
            query = """
                INSERT INTO "Project" (name, "userInput", type, "repoUrl", "userId", "teamId", "createdAt", "updatedAt")
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING *
            """
            now = datetime.now()
            row = await conn.fetchrow(
                query, project.name, project.user_input, project.type.value,
                project.repo_url, user_id, project.team_id, now, now
            )
            return cls._row_to_project_response(row)
    
    @classmethod
    async def get_project(cls, project_id: str) -> Optional[ProjectResponse]:
        """Get project by ID"""
        async with cls.get_connection() as conn:
            query = 'SELECT * FROM "Project" WHERE id = $1'
            row = await conn.fetchrow(query, project_id)
            return cls._row_to_project_response(row) if row else None
    
    @classmethod
    async def get_user_projects(cls, user_id: str) -> List[ProjectResponse]:
        """Get all projects for a user"""
        async with cls.get_connection() as conn:
            query = 'SELECT * FROM "Project" WHERE "userId" = $1 ORDER BY "createdAt" DESC'
            rows = await conn.fetch(query, user_id)
            return [cls._row_to_project_response(row) for row in rows]

    # Project Overview operations
    @classmethod
    async def create_project_overview(cls, overview: ProjectOverviewCreate) -> ProjectOverviewResponse:
        """Create project overview"""
        async with cls.get_connection() as conn:
            query = """
                INSERT INTO "ProjectOverview" (content, "userFlow", "techStack", "projectId", "createdAt", "updatedAt")
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """
            now = datetime.now()
            row = await conn.fetchrow(
                query, overview.content, overview.user_flow,
                json.dumps(overview.tech_stack), overview.project_id, now, now
            )
            return cls._row_to_overview_response(row)
    
    @classmethod
    async def get_project_overview(cls, project_id: str) -> Optional[ProjectOverviewResponse]:
        """Get project overview"""
        async with cls.get_connection() as conn:
            query = 'SELECT * FROM "ProjectOverview" WHERE "projectId" = $1'
            row = await conn.fetchrow(query, project_id)
            return cls._row_to_overview_response(row) if row else None
    
    @classmethod
    async def update_project_overview(cls, project_id: str, content: str = None, 
                                    user_flow: str = None, tech_stack: Dict = None) -> Optional[ProjectOverviewResponse]:
        """Update project overview"""
        async with cls.get_connection() as conn:
            update_fields = []
            params = []
            param_count = 1
            
            if content:
                update_fields.append(f'content = ${param_count}')
                params.append(content)
                param_count += 1
            
            if user_flow:
                update_fields.append(f'"userFlow" = ${param_count}')
                params.append(user_flow)
                param_count += 1
            
            if tech_stack:
                update_fields.append(f'"techStack" = ${param_count}')
                params.append(json.dumps(tech_stack))
                param_count += 1
            
            if not update_fields:
                return None
            
            update_fields.append(f'"updatedAt" = ${param_count}')
            params.append(datetime.now())
            params.append(project_id)
            
            query = f'''
                UPDATE "ProjectOverview" 
                SET {", ".join(update_fields)}
                WHERE "projectId" = ${param_count + 1}
                RETURNING *
            '''
            
            row = await conn.fetchrow(query, *params)
            return cls._row_to_overview_response(row) if row else None

    # Flowchart operations
    @classmethod
    async def create_flowchart_state(cls, flowchart: FlowchartStateCreate) -> FlowchartStateResponse:
        """Create flowchart state"""
        async with cls.get_connection() as conn:
            query = """
                INSERT INTO "FlowchartState" ("flowchartJson", "changeDescription", "projectId", "createdAt")
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """
            row = await conn.fetchrow(
                query, json.dumps(flowchart.flowchart_json.dict()),
                flowchart.change_description, flowchart.project_id, datetime.now()
            )
            return cls._row_to_flowchart_response(row)
    
    @classmethod
    async def get_latest_flowchart(cls, project_id: str) -> Optional[FlowchartStateResponse]:
        """Get latest flowchart state for project"""
        async with cls.get_connection() as conn:
            query = '''
                SELECT * FROM "FlowchartState" 
                WHERE "projectId" = $1 
                ORDER BY "createdAt" DESC 
                LIMIT 1
            '''
            row = await conn.fetchrow(query, project_id)
            return cls._row_to_flowchart_response(row) if row else None
    
    @classmethod
    async def get_flowchart_history(cls, project_id: str) -> List[FlowchartStateResponse]:
        """Get flowchart history for project"""
        async with cls.get_connection() as conn:
            query = '''
                SELECT * FROM "FlowchartState" 
                WHERE "projectId" = $1 
                ORDER BY "createdAt" DESC
            '''
            rows = await conn.fetch(query, project_id)
            return [cls._row_to_flowchart_response(row) for row in rows]

    # File operations
    @classmethod
    async def create_file_node(cls, file_node: FileNodeCreate) -> FileNodeResponse:
        """Create file node"""
        async with cls.get_connection() as conn:
            query = """
                INSERT INTO "FileNode" (name, path, type, "generatedCode", explanation, "projectId", "parentId", "createdAt", "updatedAt")
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING *
            """
            now = datetime.now()
            row = await conn.fetchrow(
                query, file_node.name, file_node.path, file_node.type.value,
                file_node.generated_code, file_node.explanation,
                file_node.project_id, file_node.parent_id, now, now
            )
            return cls._row_to_file_node_response(row)
    
    @classmethod
    async def get_project_file_structure(cls, project_id: str) -> List[FileNodeResponse]:
        """Get file structure for project"""
        async with cls.get_connection() as conn:
            query = 'SELECT * FROM "FileNode" WHERE "projectId" = $1 ORDER BY path'
            rows = await conn.fetch(query, project_id)
            return [cls._row_to_file_node_response(row) for row in rows]
    
    @classmethod
    async def update_file_node(cls, file_id: str, generated_code: str = None, 
                             explanation: str = None) -> Optional[FileNodeResponse]:
        """Update file node"""
        async with cls.get_connection() as conn:
            update_fields = []
            params = []
            param_count = 1
            
            if generated_code is not None:
                update_fields.append(f'"generatedCode" = ${param_count}')
                params.append(generated_code)
                param_count += 1
            
            if explanation is not None:
                update_fields.append(f'explanation = ${param_count}')
                params.append(explanation)
                param_count += 1
            
            if not update_fields:
                return None
            
            update_fields.append(f'"updatedAt" = ${param_count}')
            params.append(datetime.now())
            params.append(file_id)
            
            query = f'''
                UPDATE "FileNode" 
                SET {", ".join(update_fields)}
                WHERE id = ${param_count + 1}
                RETURNING *
            '''
            
            row = await conn.fetchrow(query, *params)
            return cls._row_to_file_node_response(row) if row else None

    # Uploaded files operations
    @classmethod
    async def create_uploaded_file(cls, uploaded_file: UploadedFileCreate) -> UploadedFileResponse:
        """Create uploaded file record"""
        async with cls.get_connection() as conn:
            query = """
                INSERT INTO "UploadedFile" (path, content, "projectId", "createdAt")
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """
            row = await conn.fetchrow(
                query, uploaded_file.path, uploaded_file.content,
                uploaded_file.project_id, datetime.now()
            )
            return cls._row_to_uploaded_file_response(row)
    
    @classmethod
    async def get_uploaded_files(cls, project_id: str) -> List[UploadedFileResponse]:
        """Get uploaded files for project"""
        async with cls.get_connection() as conn:
            query = 'SELECT * FROM "UploadedFile" WHERE "projectId" = $1 ORDER BY path'
            rows = await conn.fetch(query, project_id)
            return [cls._row_to_uploaded_file_response(row) for row in rows]

    # Message operations
    @classmethod
    async def create_message(cls, message: MessageCreate) -> MessageResponse:
        """Create message"""
        async with cls.get_connection() as conn:
            query = """
                INSERT INTO "Message" (content, role, "projectId", "createdAt")
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """
            row = await conn.fetchrow(
                query, message.content, message.role.value,
                message.project_id, datetime.now()
            )
            return cls._row_to_message_response(row)
    
    @classmethod
    async def get_project_messages(cls, project_id: str, limit: int = 50) -> List[MessageResponse]:
        """Get messages for project"""
        async with cls.get_connection() as conn:
            query = '''
                SELECT * FROM "Message" 
                WHERE "projectId" = $1 
                ORDER BY "createdAt" DESC 
                LIMIT $2
            '''
            rows = await conn.fetch(query, project_id, limit)
            return [cls._row_to_message_response(row) for row in rows]

    # Helper methods to convert database rows to response models
    @staticmethod
    def _row_to_user_response(row) -> UserResponse:
        return UserResponse(
            id=row['id'],
            email=row['email'],
            username=row['username'],
            plan=Plan(row['plan']),
            project_count_this_month=row['projectCountThisMonth'],
            repo_analysis_count_this_month=row['repoAnalysisCountThisMonth'],
            created_at=row['createdAt'],
            updated_at=row['updatedAt']
        )
    
    @staticmethod
    def _row_to_project_response(row) -> ProjectResponse:
        return ProjectResponse(
            id=row['id'],
            name=row['name'],
            user_input=row['userInput'],
            type=ProjectType(row['type']),
            repo_url=row['repoUrl'],
            user_id=row['userId'],
            team_id=row['teamId'],
            created_at=row['createdAt'],
            updated_at=row['updatedAt']
        )
    
    @staticmethod
    def _row_to_overview_response(row) -> ProjectOverviewResponse:
        return ProjectOverviewResponse(
            id=row['id'],
            content=row['content'],
            user_flow=row['userFlow'],
            tech_stack=json.loads(row['techStack']) if row['techStack'] else {},
            project_id=row['projectId'],
            created_at=row['createdAt'],
            updated_at=row['updatedAt']
        )
    
    @staticmethod
    def _row_to_flowchart_response(row) -> FlowchartStateResponse:
        from models.schemas import FlowchartData
        return FlowchartStateResponse(
            id=row['id'],
            flowchart_json=FlowchartData(**json.loads(row['flowchartJson'])),
            change_description=row['changeDescription'],
            project_id=row['projectId'],
            created_at=row['createdAt']
        )
    
    @staticmethod
    def _row_to_file_node_response(row) -> FileNodeResponse:
        return FileNodeResponse(
            id=row['id'],
            name=row['name'],
            path=row['path'],
            type=NodeType(row['type']),
            generated_code=row['generatedCode'],
            explanation=row['explanation'],
            project_id=row['projectId'],
            parent_id=row['parentId'],
            created_at=row['createdAt'],
            updated_at=row['updatedAt']
        )
    
    @staticmethod
    def _row_to_uploaded_file_response(row) -> UploadedFileResponse:
        return UploadedFileResponse(
            id=row['id'],
            path=row['path'],
            content=row['content'],
            project_id=row['projectId'],
            created_at=row['createdAt']
        )
    
    @staticmethod
    def _row_to_message_response(row) -> MessageResponse:
        return MessageResponse(
            id=row['id'],
            content=row['content'],
            role=Role(row['role']),
            project_id=row['projectId'],
            created_at=row['createdAt']
        )