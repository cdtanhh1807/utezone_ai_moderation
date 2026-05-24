from abc import ABC, abstractmethod
from typing import List, Optional

from dto.ban.request.get_all_ban_request import GetAllBanRequest
from dto.ban.response.get_all_ban_response import GetAllBanResponse


class IBanService(ABC):
    
    @abstractmethod
    async def get_all(self, ban_list: GetAllBanRequest) -> Optional[List[GetAllBanResponse]]:
        pass