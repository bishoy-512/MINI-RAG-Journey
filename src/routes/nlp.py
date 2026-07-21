from fastapi import FastAPI, APIRouter , Request , status
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest , SearchRequest
from models import ProjectModel , ChunkModel
from controllers import NLPController
from models.Enum import ResponseEnum
import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(prefix="/api/v1/nlp",tags=["api_v1" , "nlp"])


@nlp_router.post("/index/push/{project_id}")
async def index_project(request : Request , project_id : str, push_request : PushRequest):
    
    project_model = await ProjectModel.create_instance(db_client = request.app.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "Response":ResponseEnum.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        embedding_client=request.app.emb_client,
        vectorDB_client=request.app.vectorDB_client,
    )
    
    has_records = True
    page_no = 1
    inserted_chunks_count = 0
    idx = 0
    
    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id = project.id , page_no = page_no)
        
        if len(page_chunks):
            page_no += 1
            
        if len(page_chunks) == 0 or not page_chunks:
            has_records = False
            break
        
        chunks_ids = list(range(idx , idx + len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            chunks_ids=chunks_ids
        )
        
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "Response" : ResponseEnum.INSERT_INTO_VECTORDB_ERROR.value
                }
            )
        inserted_chunks_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "Response" : ResponseEnum.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_chunks_count
        }
    )
    
    
@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request : Request , project_id : str):
    
    project_model = await ProjectModel.create_instance(db_client = request.app.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)
    
    nlp_controller = NLPController(
        generation_client=request.app.generation_client,
        embedding_client=request.app.emb_client,
        vectorDB_client=request.app.vectorDB_client,
    )
    
    collection_info = nlp_controller.get_vector_db_collection_info(project=project)
    
    return JSONResponse(
            content={
                "Response" : ResponseEnum.VECTORDB_COLLECTION_RETRIEVED.value,
                "Collection Info" : collection_info
            }
        )
    
@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_project(project_id=project_id)

    nlp_controller = NLPController(
        vectorDB_client=request.app.vectorDB_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.emb_client,
    )

    results = nlp_controller.search_vector_db_collection(project=project, text=search_request.text, limit=search_request.limit)

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseEnum.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
        content={
            "signal": ResponseEnum.VECTORDB_SEARCH_SUCCESS.value,
            "results": [ result.model_dump() for result in results ]
        }
    )