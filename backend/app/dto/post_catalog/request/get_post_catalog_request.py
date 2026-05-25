from pydantic import BaseModel


class GetPostCatalogRequest(BaseModel):
    email: str


