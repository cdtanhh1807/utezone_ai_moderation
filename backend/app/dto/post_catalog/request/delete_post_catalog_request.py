from pydantic import BaseModel


class DeletePostCatalogRequest(BaseModel):
    post_id: str
