from typing import Optional

from pydantic import BaseModel


class FindByEmailRequest(BaseModel):
    email: Optional[str] = None