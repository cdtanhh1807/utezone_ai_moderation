from abc import ABC, abstractmethod
from typing import Optional

from dto.search.request.search_account_request import SearchAccountRequest
from dto.search.request.search_post_request import SearchPostRequest
from dto.search.response.search_account_response import SearchAccountResponse
from dto.search.response.search_post_response import SearchPostResponse


class ISearchService(ABC):
    
    @abstractmethod
    async def search_account(self, req: SearchAccountRequest) -> Optional[SearchAccountResponse]:
        pass

    @abstractmethod
    async def search_post(self, req: SearchPostRequest) -> Optional[SearchPostResponse]:
        pass
