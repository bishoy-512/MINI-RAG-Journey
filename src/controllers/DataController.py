from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseEnum
from .ProjectController import ProjectController
import re
import os
class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
    
    # Validate That If We Can Use This File Or What
    def Validate_Uploaded_file(self , file : UploadFile):
    # Check If We Support This File Extension Or No
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False , ResponseEnum.FILE_TYPE_NOT_SUPPORTED.value
    # Check File Size Not More Than 10MB For Example
        if file.size > self.app_settings.FILE_MAX_SIZE * 1024:
            return False , ResponseEnum.FILE_SIZE_EXCEEDED.value
        return True , ResponseEnum.FILE_VALIDATED_SUCCESS.value
    
    def generate_unique_filename(self , orig_filename : str , project_id : str):
        # Call That Function In BaseController
        random_filename = self.generate_random_string()
        # Get Project Path To Use It To Get The New_file_Path
        project_path = ProjectController().get_project_path(project_id)
        # This Is Original File Name But Without (_ , $ % !)
        cleaned_filename = self.clean_filename(orig_filename)
        # New File Path = (Project_path + Key + File_name) (Key + File_name = File_ID)
        new_file_path = os.path.join(project_path , random_filename + "_" + cleaned_filename)
        # If Happen And We Got File Path Is Already Exist We Try To Get New Key
        while os.path.exists(new_file_path):
            random_filename = self.generate_random_string()
            new_file_path = os.path.join(project_path , random_filename + "_" + cleaned_filename)
        # Return File_Path + File_ID
        return new_file_path , random_filename + "_" + cleaned_filename
    
    def clean_filename(self , file_name:str):
        cleaned_filename = re.sub(r'[^\w.]' , '' , file_name.strip())
        cleaned_filename = cleaned_filename.replace(" " , "_")
        return cleaned_filename