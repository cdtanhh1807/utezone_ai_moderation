from pydantic import BaseModel
from typing import List
from models.announce_model import Announce


class GetAllAnnounceResponse(BaseModel):
    announce_list: List[Announce]


