from abc import ABC, abstractmethod
from typing import Optional
from dto.post.request.add_post_request import AddPostRequest
from dto.post.request.get_my_post_request import GetMyPostRequest
from dto.post.request.get_post_by_email_request import GetPostByEmailRequest
from dto.post.request.get_post_request import GetPostRequest
from dto.post.request.get_post_suggest_request import GetPostSuggestRequest
from dto.post.response.add_post_response import AddPostResponse 
from dto.post.response.get_post_by_email_response import GetPostByEmailResponse
from dto.post.response.get_post_response import GetPostResponse
from dto.post.request.update_post_request import UpdatePostRequest
from dto.post.response.get_post_suggest_response import GetPostSuggestResponse
from dto.post.response.update_post_response import UpdatePostResponse
from dto.post.request.get_all_post_request import GetAllPostRequest
from dto.post.response.get_all_post_response import GetAllPostResponse 
from dto.post.request.delete_post_request import DeletePostRequest
from dto.post.response.delete_post_response import DeletePostResponse
from dto.statistic.request.get_post_of_day_request import GetPostOfDayRequest
from dto.statistic.request.get_top_interacted_post_request import GetTopInteractedPostRequest
from dto.statistic.response.get_post_of_day_response import GetPostOfDayResponse
from dto.statistic.response.get_top_interacted_post_response import GetTopInteractedPostReponse


class IPostService(ABC):

    @abstractmethod
    async def add(self, post_req: AddPostRequest) -> Optional[AddPostResponse]:
        pass

    @abstractmethod
    async def get_all(self, post_list: GetAllPostRequest) -> GetAllPostResponse:
        pass

    @abstractmethod
    async def get_by_id(self, post_id: GetPostRequest) -> Optional[GetPostResponse]:
        pass

    @abstractmethod
    async def update(self, post_req: UpdatePostRequest) -> Optional[UpdatePostResponse]:
        pass

    @abstractmethod
    async def delete(self, post_id: DeletePostRequest) -> Optional[DeletePostResponse]:
        pass

    @abstractmethod
    async def update_comment_status(self, post_id: str, comment_id: str, status_comment: str):
        pass


    @abstractmethod
    async def find_by_id(self, post_id: str):
        pass
    
    @abstractmethod
    async def update_react(self, post_id: str, react: dict):
        pass

    @abstractmethod
    async def get_by_email(self, req: GetPostByEmailRequest) -> GetPostByEmailResponse:
        pass

    @abstractmethod
    async def get_my_post(self, post_list: GetMyPostRequest) -> GetAllPostResponse:
        pass

    @abstractmethod
    async def get_post_of_day(self, req: GetPostOfDayRequest) -> GetPostOfDayResponse:
        pass

    @abstractmethod
    async def get_top_interacted_posts_in_week(self, req: GetTopInteractedPostRequest) -> GetTopInteractedPostReponse:
        pass

    @abstractmethod
    async def get_post_suggest(self, req: GetPostSuggestRequest) -> GetPostSuggestResponse:
        pass

    @abstractmethod
    async def get_post_hidden_by_email(self, req: GetMyPostRequest) -> GetAllPostResponse:
        pass