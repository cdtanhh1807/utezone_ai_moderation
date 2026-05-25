from abc import ABC, abstractmethod
from typing import Optional

from dto.post_catalog.request.add_post_catalog_request import AddPostCatalogRequest
from dto.post_catalog.request.delete_post_catalog_request import DeletePostCatalogRequest
from dto.post_catalog.request.find_post_catalog_request import FindPostCatalogRequest
from dto.post_catalog.request.get_my_post_catalog_request import GetMyPostCatalogRequest
from dto.post_catalog.request.get_post_catalog_request import GetPostCatalogRequest
from dto.post_catalog.request.update_post_catalog_request import UpdatePostCatalogRequest
from dto.post_catalog.response.add_post_catalog_response import AddPostCatalogResponse
from dto.post_catalog.response.delete_post_catalog_response import DeletePostCatalogResponse
from dto.post_catalog.response.find_post_catalog_response import FindPostCatalogResponse
from dto.post_catalog.response.get_my_post_catalog_response import GetMyPostCatalogResponse
from dto.post_catalog.response.get_post_catalog_response import GetPostCatalogResponse
from dto.post_catalog.response.update_post_catalog_response import UpdatePostCatalogResponse

class IPostCatalogService(ABC):

    @abstractmethod
    async def add_post_catalog(self, req: AddPostCatalogRequest) -> AddPostCatalogResponse:
        pass

    @abstractmethod
    async def update_post_catalog(self, req: UpdatePostCatalogRequest) -> UpdatePostCatalogResponse:
        pass

    @abstractmethod
    async def find_post_catalog(self, req: FindPostCatalogRequest) -> FindPostCatalogResponse:
        pass

    @abstractmethod
    async def delete_post_catalog(self, req: DeletePostCatalogRequest) -> DeletePostCatalogResponse:
        pass

    @abstractmethod
    async def get_my_post_catalog(self, req: GetMyPostCatalogRequest) -> GetMyPostCatalogResponse:
        pass

    @abstractmethod
    async def get_post_catalog(self, req: GetPostCatalogRequest) -> GetPostCatalogResponse:
        pass