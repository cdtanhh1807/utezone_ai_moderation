from abc import ABC, abstractmethod
from typing import List, Optional

from dto.announce.request.get_all_announce_request import GetAllAnnounceRequest
from dto.announce.request.send_announce_request import SendAnnounceRequest
from dto.announce.response.get_all_announce_response import GetAllAnnounceResponse
from dto.announce.response.send_announce_response import SendAnnounceResponse

class IAnnounceService(ABC):
    
    @abstractmethod
    async def get_all_by_receiver_email(self, req: GetAllAnnounceRequest) -> Optional[GetAllAnnounceResponse]:
        pass

    @abstractmethod
    async def add(self, req: SendAnnounceRequest) -> Optional[SendAnnounceResponse]:
        pass
