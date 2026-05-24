from pydantic import BaseModel


class FollowBlockResponse(BaseModel):
    message: str
    success: bool