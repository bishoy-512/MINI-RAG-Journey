from helpers.config import get_settings , Settings
import os
import string
import random

class BaseController:
    # That The Main Controller That Others Inherit From It
    # It Has The Base Dir Path (The Main Folder Path Based On Urs PC)
    # Got The Path Of Where Files Will Save (Assets => Files)
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.files_dir = os.path.join(self.base_dir , "assets" , "files")
    # It Generate A Unique String We Use It As A key In Process Controller (Put It Before File Name)
    def generate_random_string(self , length:int=10):
        return ''.join(random.choices(string.ascii_lowercase + string.digits , k = length))