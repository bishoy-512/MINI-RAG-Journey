from .BaseDataModel import BaseDataModel
from .db_schemes.Project import Project
from .Enum.DataBaseEnum import DataBaseEnum
class ProjectModel(BaseDataModel):
    
    def __init__(self, db_client):
        super().__init__(db_client)
        # Get DB Collection (Like Table In SQL) That I Work On It
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
    
    async def create_project(self , project : Project):
        # Create New Project In DB And Return It's ID
        result = await self.collection.insert_one(project.dict())
        project.id = result.inserted_id
        return project
    
    async def get_or_create_project(self , project_id : str):
        # Search In DB For Project With Project_ID
        record = await self.collection.find_one({"project_id" : project_id})
        # If Found it, just return it else create new project
        if record is None:
            project = Project(project_id = project_id)
            project = await self.create_project(project=project)
            return project
        # Convert Record (Dict) to Project Model
        return Project(**record)
    
    async def get_all_projects(self, page: int=1, page_size: int=10):
        # count total number of documents
        total_documents = await self.collection.count_documents({})
        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
            total_pages += 1
        cursor = self.collection.find().skip( (page-1) * page_size ).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        return projects, total_pages
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME not in all_collections:
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"] , name=index["name"] , unique=index["unique"])
    
    @classmethod
    async def create_instance(cls , db_client : object):
        instance = cls(db_client = db_client)
        await instance.init_collection()
        return instance