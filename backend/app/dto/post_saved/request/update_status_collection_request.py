from typing import Optional

from pydantic import BaseModel

class UpdateStatusCollectionRequest(BaseModel):
    email: Optional[str] = None
    collection_name: str
    status: str