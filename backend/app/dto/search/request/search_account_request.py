from pydantic import BaseModel


class SearchAccountRequest(BaseModel):
    email: str
    keySearch: str
    

