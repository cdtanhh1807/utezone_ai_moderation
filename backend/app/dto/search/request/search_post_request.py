from pydantic import BaseModel


class SearchPostRequest(BaseModel):
    email: str
    keySearch: str


