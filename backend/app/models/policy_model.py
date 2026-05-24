from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId

class Action(BaseModel):
    permission: str
    detail: str

class Policy(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    description: str
    level: int
    status: str
    createdAt: datetime
    updatedAt: datetime
    action: Optional[Action] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
