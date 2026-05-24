from pydantic import BaseModel


class GetAllAnnounceRequest(BaseModel):
    email: str


