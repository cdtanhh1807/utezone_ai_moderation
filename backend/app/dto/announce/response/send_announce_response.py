from pydantic import BaseModel

from models.announce_model import Announce


class SendAnnounceResponse(BaseModel):
    announce: Announce


