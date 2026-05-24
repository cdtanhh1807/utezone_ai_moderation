from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId
from models.policy_model import Action


class UpdatePolicyRequest(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    status: Optional[str] = None
    action: Optional[Action] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
