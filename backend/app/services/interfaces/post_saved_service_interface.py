from abc import ABC, abstractmethod
from typing import Optional

from dto.post_saved.request.add_collection_request import AddCollectionRequest
from dto.post_saved.request.add_post_to_collection_request import AddPostToCollectionRequest
from dto.post_saved.request.delete_collection_request import DeleteCollectionRequest
from dto.post_saved.request.find_by_email_request import FindByEmailRequest
from dto.post_saved.request.remove_post_from_collection_request import RemovePostFromCollectionRequest
from dto.post_saved.request.rename_collection_request import RenameCollectionRequest
from dto.post_saved.request.update_status_collection_request import UpdateStatusCollectionRequest
from dto.post_saved.response.add_collection_response import AddCollectionResponse
from dto.post_saved.response.add_post_to_collection_response import AddPostToCollectionResponse
from dto.post_saved.response.delete_collection_response import DeleteCollectionResponse
from dto.post_saved.response.find_by_email_response import FindByEmailResponse
from dto.post_saved.response.remove_post_from_collection_response import RemovePostFromCollectionResponse
from dto.post_saved.response.rename_collection_response import RenameCollectionResponse
from dto.post_saved.response.update_status_collection_response import UpdateStatusCollectionResponse

class IPostSavedService(ABC):

    @abstractmethod
    async def add_collection(self, req: AddCollectionRequest) -> AddCollectionResponse:
        pass

    @abstractmethod
    async def add_post_to_collection(self, req: AddPostToCollectionRequest) -> AddPostToCollectionResponse:
        pass
    
    @abstractmethod
    async def remove_post_from_collection(self, req: RemovePostFromCollectionRequest) -> RemovePostFromCollectionResponse:
        pass

    @abstractmethod
    async def delete_collection(self, req: DeleteCollectionRequest) -> DeleteCollectionResponse:
        pass

    @abstractmethod
    async def find_by_email(self, req: FindByEmailRequest) -> FindByEmailResponse:
        pass

    @abstractmethod
    async def rename_collection(self, req: RenameCollectionRequest) -> RenameCollectionResponse:
        pass

    @abstractmethod
    async def update_status_collection(self, req: UpdateStatusCollectionRequest) -> UpdateStatusCollectionResponse:
        pass