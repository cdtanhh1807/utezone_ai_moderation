from pydantic import BaseModel, Field

class MarkReadRequest(BaseModel):
    other_email: str = Field(..., description="Email của người còn lại trong cuộc trò chuyện")