from fastapi import APIRouter, HTTPException
from services.database import Database
from models.schemas import ProjectResponse
from typing import List

router = APIRouter()

@router.get("/projects")
async def get_projects() -> List[ProjectResponse]:
    """Get all projects for user"""
    try:
        # In production, get user_id from auth
        user_id = "temp_user"
        projects = await Database.get_user_projects(user_id)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str) -> ProjectResponse:
    """Get specific project"""
    project = await Database.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project