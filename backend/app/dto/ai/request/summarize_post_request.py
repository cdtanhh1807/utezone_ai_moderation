from pydantic import BaseModel, Field


class SummarizePostRequest(BaseModel):
    post_id: str = Field(..., description="ID của bài viết cần tóm tắt")
    force_refresh: bool = Field(default=False, description="Bỏ qua cache và tóm tắt lại")
    
    class Config:
        json_schema_extra = {
            "example": {
                "post_id": "69b00ff03db9330888881bef",
                "force_refresh": False
            }
        }