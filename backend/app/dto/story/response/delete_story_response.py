from pydantic import BaseModel

class DeleteStoryResponse(BaseModel):
    success: bool
    message: str
