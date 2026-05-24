from pydantic import BaseModel
from typing import List, Optional


class SuggestFollowItem(BaseModel):
    id: str
    email: str
    fullName: Optional[str] = None
    department: Optional[str] = None
    avatar: Optional[str] = None
    description: Optional[str] = None
    interaction_score: int = 0
    posts_count: int = 0
    comments_count: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "id": "69e677c0b16e796c3c6bbb45",
                "email": "cdtanhh@gmail.com",
                "fullName": "Liam Cao",
                "department": "CÔNG NGHỆ THÔNG TIN",
                "avatar": None,
                "description": "Xin chào",
                "interaction_score": 15,
                "posts_count": 3,
                "comments_count": 12
            }
        }

class SuggestFollowResponse(BaseModel):
    suggestions: List[SuggestFollowItem]