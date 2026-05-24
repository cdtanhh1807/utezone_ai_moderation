from typing import Optional

from pydantic import BaseModel

class DeleteCollectionRequest(BaseModel):
    email: Optional[str] = None
    collection_name: Optional[str] = None