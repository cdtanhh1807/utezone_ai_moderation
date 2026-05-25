from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FindPostCatalogRequest(BaseModel):
    post_id: str

