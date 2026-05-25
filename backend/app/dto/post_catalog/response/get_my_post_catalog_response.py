from pydantic import BaseModel
from typing import List
from models.post_catalog_model import PostCatalog 

class GetMyPostCatalogResponse(BaseModel):
    post_catalog_list: List[PostCatalog] = []
