from typing import Optional, List
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from models.base_model import PyObjectId
from models.account_model import UserInfo
from datetime import datetime
from models.account_model import Permission


class UpdateUserInfo(BaseModel):
    fullName: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    day_of_birth: Optional[str] = None
    followers: Optional[List[str]] = None
    limits: Optional[List[str]] = None
    blocks: Optional[List[str]] = None
    description: Optional[str] = None


class UpdateAccountRequest(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    userInfo: Optional[UpdateUserInfo] = None
    permission: Optional[Permission] = None


    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        extra = "allow"
