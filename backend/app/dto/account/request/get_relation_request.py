from pydantic import BaseModel


class GetRelationRequest(BaseModel):
    email: str
