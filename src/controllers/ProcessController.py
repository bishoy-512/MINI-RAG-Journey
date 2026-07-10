from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ProcessEnum
from langchain_community.document_loaders import TextLoader , PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class ProcessController(BaseController):
    
    def __init__(self, project_id : str):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)
    # File_ID = Key (Generate String) + File_Name 
    # It Return File Ext Like (file_id.PDF) We Make Split First With ID And Get Last Word
    def get_file_extension(self , file_id : str):
        return os.path.splitext(file_id)[-1]
    # This Function Return The Right Loader That Extract Data From File
    def get_file_loader(self , file_id : str):
        # Get File Ext
        file_ext = self.get_file_extension(file_id=file_id)
        # Get File Path That Is Consist Of (Project_Path + File_id)
        file_path = os.path.join(self.project_path , file_id)
        # If TXT Return TextLoader
        if file_ext == ProcessEnum.TXT.value:
            return TextLoader(file_path=file_path , encoding="utf-8")
        # .PDF Return PyMuPDFLoader Library
        if file_ext == ProcessEnum.PDF.value:
            return PyMuPDFLoader(file_path=file_path)
        # If not TXT Or PDF Return NONE
        return None
    
    def get_file_content(self , file_id : set):
        # Get The Right Loader From get_file_loader Fun Then Execute It
        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()
        return None
    
    def process_file_content(self , file_content : list , chunk_size : int = 100 , overlap_size : int = 20):
        # Get Splitter Model Text Depend On My Chunk_Size and Overlap_size
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size , chunk_overlap = overlap_size)
        # Any File Content Contain (Page_Content And MetaData)
        # Page_Content ("Python is easy...") , MetaData ("source":"python.pdf" , "page":5)
        # So We Split Each One In List
        file_content_texts = [rec.page_content for rec in file_content]
        file_content_metadata = [rec.metadata for rec in file_content]
        # Here We Use Text Splitter Model To Split Text Into Chunks
        chunks = text_splitter.create_documents(texts=file_content_texts , metadatas=file_content_metadata)
        return chunks