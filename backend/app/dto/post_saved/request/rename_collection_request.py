from typing import Optional

from pydantic import BaseModel

class RenameCollectionRequest(BaseModel):
    email: Optional[str] = None
    old_name: str
    new_name: str