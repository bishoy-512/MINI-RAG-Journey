from fastapi import FastAPI, APIRouter , Depends , UploadFile , status
from fastapi.responses import JSONResponse
from helpers.config import get_settings , Settings
from controllers.DataController import DataController
from controllers.ProjectController import ProjectController
from models.Enum.ResponseEnum import ResponseEnum
import aiofiles
import os
import logging
logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1" , "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id : str , file : UploadFile , app_settings : Settings = Depends(get_settings)):
    is_valid , MSG = DataController().Validate_Uploaded_file(file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST , content={"Response":MSG})
    project_dir_path = ProjectController().get_project_path(project_id)
    file_path , file_id = DataController().generate_unique_filename(file.filename , project_id = project_id)
    try:
        async with aiofiles.open(file_path , "wb") as f:
            while chunk := await file.read(app_settings.FILE_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error While Uploading File: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST , content={"Result":ResponseEnum.FILE_UPLOAD_FAILED})
            
    return {
        "Response" : ResponseEnum.FILE_UPLOAD_SUCCESS.value,
        "File ID" : file_id
    }

