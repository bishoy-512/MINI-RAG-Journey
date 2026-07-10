from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    # This Config Because Pydantic Can't Work With [ObjectId] So This Class Mean Skip This
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    # This Is Project Scheme That Must All Records Have The Same Fields
    # _id => It's ID That's Come Automatic From [ObjectId] 
    id: Optional[ObjectId] = Field(None, alias="_id")
    
    # This Is Real Project ID
    project_id : str = Field(... , min_length=1)
    
    # Validate That ID Is Alpha Numerical 
    @field_validator('project_id')
    def validate_project_id(cls , value):
        if not value.isalnum():
            raise ValueError("project id must be alpha numeric value")
        return value
    
    @classmethod
    def get_indexes(cls):
        return [
                {
                    "key" : [("project_id" , 1)] ,
                    "name" : "project_id_index_1" ,
                    "unique" : True
                }
            ]
    