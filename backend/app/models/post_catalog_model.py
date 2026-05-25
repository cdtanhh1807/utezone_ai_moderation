from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from models.base_model import PyObjectId
from bson import ObjectId
from models.post_model import Post

class PostCatalog(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    post_id: str
    email: str
    begin_at: datetime = Field(default_factory=datetime.now)
    end_at: datetime
    
    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}