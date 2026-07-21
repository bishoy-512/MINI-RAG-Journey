from fastapi import FastAPI
from routes import base , data , nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores import VectorDBProviderFactory

app = FastAPI()

@app.on_event("startup")
async def startup():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    
    llm_provide_factory = LLMProviderFactory(settings)
    vectorDB_provide_factory = VectorDBProviderFactory(settings)
    
    app.generation_client = llm_provide_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    
    app.emb_client = llm_provide_factory.create(provider=settings.EMBEDDING_BACKEND) 
    app.emb_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID , embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    app.vectorDB_client = vectorDB_provide_factory.create(settings.VECTOR_DB_BACKEND)
    app.vectorDB_client.connect()
    
    
@app.on_event("shutdown")
async def shutdown():
    app.mongo_conn.close()
    app.vectorDB_client.disconnect()

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
