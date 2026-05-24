from pydantic import BaseModel, Field
from typing import Optional


class ModerateContentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Nội dung cần kiểm duyệt (bài đăng hoặc comment)")
    content_type: str = Field(default="post", pattern="^(post|comment)$", description="Loại nội dung: post hoặc comment")
    author_id: Optional[str] = Field(default=None, description="ID của người đăng (để tracking)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Nội dung bài đăng hoặc bình luận cần kiểm tra...",
                "content_type": "post",
                "author_id": "user_123"
            }
        }