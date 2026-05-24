from bson import ObjectId
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from models.policy_model import Action


class AddPolicyRequest(BaseModel):
    name: str
    description: str
    level: int
    status: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        extra = "allow"
