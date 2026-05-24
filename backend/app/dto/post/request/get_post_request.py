from pydantic import BaseModel


class GetPostRequest(BaseModel):
    id: str


