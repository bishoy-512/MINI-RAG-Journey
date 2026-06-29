from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseEnum
from .ProjectController import ProjectController
import re
import os
class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
    
    def Validate_Uploaded_file(self , file : UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False , ResponseEnum.FILE_TYPE_NOT_SUPPORTED.value
        if file.size > self.app_settings.FILE_MAX_SIZE * 1024:
            return False , ResponseEnum.FILE_SIZE_EXCEEDED.value
        return True , ResponseEnum.FILE_VALIDATED_SUCCESS.value
    
    def generate_unique_filename(self , orig_filename : str , project_id : str):
        
        random_filename = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id)
        cleaned_filename = self.clean_filename(orig_filename)
        new_file_path = os.path.join(project_path , random_filename + "_" + cleaned_filename)
        while os.path.exists(new_file_path):
            random_filename = self.generate_random_string()
            new_file_path = os.path.join(project_path , random_filename + "_" + cleaned_filename)
        return new_file_path , random_filename + "_" + cleaned_filename
    
    def clean_filename(self , file_name:str):
        cleaned_filename = re.sub(r'[^\w.]' , '' , file_name.strip())
        cleaned_filename = cleaned_filename.replace(" " , "_")
        return cleaned_filename