from pydantic import BaseModel
from typing import List, Optional

class AccountInfoResponse(BaseModel):
    fullName: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    day_of_birth: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    followers: Optional[List[str]] = []
    followed: Optional[List[str]] = []
    blocks: Optional[List[str]] = []
    department: Optional[str] = None