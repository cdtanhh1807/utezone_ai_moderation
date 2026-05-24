from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId

class Detail(BaseModel):
    blocker: str
    at: datetime

class Violation(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    policyId: str
    violatorEmail: str
    updatedAt: Optional[List[Detail]] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
