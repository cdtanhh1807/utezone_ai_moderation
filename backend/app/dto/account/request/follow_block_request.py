from pydantic import BaseModel

class FollowBlockRequest(BaseModel):
    owner: str
    client: str