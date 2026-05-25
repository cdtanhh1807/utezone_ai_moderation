from typing import Optional
from models.post_catalog_model import PostCatalog
from pydantic import BaseModel


class FindPostCatalogResponse(BaseModel):
    post_catalog: Optional[PostCatalog]