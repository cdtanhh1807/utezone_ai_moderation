from pydantic import BaseModel


class SendAnnounceRequest(BaseModel):
    receiverEmail: str


