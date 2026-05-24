from pydantic import BaseModel


class AddPostResponse(BaseModel):
    success: bool
    message: str
