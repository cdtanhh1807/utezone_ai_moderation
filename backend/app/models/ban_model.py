from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime
from models.base_model import PyObjectId
from bson import ObjectId

class Violation(BaseModel):
    violationId: str
    beginAt: datetime
    endAt: datetime

class Ban(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    violatorEmail: str
    violations: Optional[List[Violation]] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
