from pydantic import BaseModel, Field
from typing import Optional, List

class ModerationScores(BaseModel):
    toxicity: float = Field(default=0.0, ge=0.0, le=1.0)
    insult: float = Field(default=0.0, ge=0.0, le=1.0)
    hate_speech: float = Field(default=0.0, ge=0.0, le=1.0)
    harassment: float = Field(default=0.0, ge=0.0, le=1.0)
    spam: float = Field(default=0.0, ge=0.0, le=1.0)
    sexual_content: float = Field(default=0.0, ge=0.0, le=1.0)
    violence: float = Field(default=0.0, ge=0.0, le=1.0)

class ModerateContentResponse(BaseModel):
    success: bool = Field(default=True)
    content_type: str = Field(...)
    approved: bool = Field(..., description="True = publish ngay, False = reject")
    scores: ModerationScores = Field(default_factory=ModerationScores)
    violated_categories: List[str] = Field(default_factory=list)
    reason: Optional[str] = Field(default=None, description="Lý do reject (nếu có)")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    error_message: Optional[str] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "content_type": "post",
                "approved": False,
                "scores": {
                    "toxicity": 0.82,
                    "insult": 0.75,
                    "hate_speech": 0.1,
                    "harassment": 0.3,
                    "spam": 0.05,
                    "sexual_content": 0.0,
                    "violence": 0.1
                },
                "violated_categories": ["toxicity", "insult"],
                "reason": "Nội dung chứa ngôn từ xúc phạm và độc hại. Vui lòng sử dụng ngôn ngữ lịch sự.",
                "confidence": 0.88
            }
        }
