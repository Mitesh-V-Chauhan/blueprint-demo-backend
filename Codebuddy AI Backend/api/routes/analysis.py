from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import zipfile
import tempfile
import os

router = APIRouter()

@router.post("/analyze-codebase")
async def analyze_uploaded_codebase(file: UploadFile = File(...)):
    """Analyze uploaded codebase"""
    try:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")
        
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Extract and analyze
        analysis_result = await _analyze_zip_file(tmp_file_path)
        
        # Cleanup
        os.unlink(tmp_file_path)
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _analyze_zip_file(zip_path: str):
    """Analyze ZIP file contents"""
    files_analyzed = []
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.filelist:
            if not file_info.is_dir() and file_info.filename.endswith(('.py', '.js', '.tsx', '.ts')):
                files_analyzed.append({
                    "path": file_info.filename,
                    "size": file_info.file_size,
                    "type": "code"
                })
    
    return {
        "total_files": len(files_analyzed),
        "files": files_analyzed[:20],  # Limit for demo
        "analysis": "Basic file structure analysis completed"
    }