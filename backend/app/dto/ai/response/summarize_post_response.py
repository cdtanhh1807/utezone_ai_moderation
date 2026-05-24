from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SummarizePostResponse(BaseModel):
    success: bool = Field(default=True)
    post_id: str
    title: str
    summary: str = Field(..., description="Nội dung đã tóm tắt")
    original_content: str
    generated_at: Optional[str] = None
    cached: bool = Field(default=False, description="Có lấy từ cache không")
    used_vision: bool = False
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "post_id": "69b00ff03db9330888881bef",
                "title": "Changgg",
                "summary": "Bài đăng chia sẻ hình ảnh về Chang đang ngủ.",
                "original_content": "Đây là Chang ngủ nè",
                "generated_at": "2026-03-10T12:00:00",
                "cached": False
            }
        }