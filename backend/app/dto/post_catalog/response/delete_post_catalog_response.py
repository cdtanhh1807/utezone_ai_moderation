from pydantic import BaseModel


class DeletePostCatalogResponse(BaseModel):
    success: bool
    message: str
