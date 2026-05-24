from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from models.base_model import PyObjectId
from bson import ObjectId


class UserInfo(BaseModel):
    fullName: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    day_of_birth: Optional[str] = None
    followers: List[str] = []
    followed: List[str] = []
    limits: List[str] = []
    blocks: List[str] = []
    description: Optional[str] = None
    avatar: Optional[str] = None
    department: Optional[str] = None

class Permission(BaseModel):
    pernum: str
    validity: datetime

class Account(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    type: Optional[str]
    email: str
    password: Optional[str]
    role: Optional[str]
    status: Optional[str] = "actice"
    userInfo: Optional[UserInfo] = None
    permission: Optional[Permission] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"