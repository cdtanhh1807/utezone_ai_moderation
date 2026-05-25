from pydantic import BaseModel
from typing import List
from models.post_catalog_model import PostCatalog 

class GetPostCatalogResponse(BaseModel):
    post_catalog_list: List[PostCatalog] = []
