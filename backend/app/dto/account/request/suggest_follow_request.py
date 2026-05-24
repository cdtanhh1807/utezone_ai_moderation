from pydantic import BaseModel

class SuggestFollowRequest(BaseModel):
    email: str
    limit: int = 20