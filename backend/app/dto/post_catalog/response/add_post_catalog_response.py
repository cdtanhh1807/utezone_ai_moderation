from pydantic import BaseModel
from models.post_catalog_model import PostCatalog


class AddPostCatalogResponse(BaseModel):
    item: PostCatalog
