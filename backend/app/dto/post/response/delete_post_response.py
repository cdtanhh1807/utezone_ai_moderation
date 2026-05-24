from pydantic import BaseModel


class DeletePostResponse(BaseModel):
    success: bool
    message: str
