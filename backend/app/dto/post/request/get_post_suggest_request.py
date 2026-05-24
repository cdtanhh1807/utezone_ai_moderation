from pydantic import BaseModel


class GetPostSuggestRequest(BaseModel):
    email: str


