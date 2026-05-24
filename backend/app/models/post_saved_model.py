from pydantic import BaseModel, Field
from typing import Optional, List
from models.base_model import PyObjectId
from bson import ObjectId

class Collection(BaseModel):
    name: str
    posts: List[str]
    status: Optional[str] = None

class PostSaved(BaseModel):  
    # id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
    collections: List[Collection]
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}