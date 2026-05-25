from pydantic import BaseModel


class GetMyPostCatalogRequest(BaseModel):
    email: str


