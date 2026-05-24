from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

class UpdateAccountTRequest(BaseModel):
    fullName: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    day_of_birth: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    department: Optional[str] = None