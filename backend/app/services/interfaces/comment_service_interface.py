from abc import ABC, abstractmethod
from dto.comment.request.add_comment_request import AddCommentRequest
from dto.comment.request.add_commentreply_request import AddCommentReplyRequest
from dto.comment.request.get_commentreply_request import GetCommentReplyRequest
from dto.comment.request.update_status_comment_reply_request import UpdateStatusCommentReplyRequest
from dto.comment.response.add_comment_response import AddCommentResponse
from dto.comment.response.add_commentreply_response import AddCommentReplyResponse
from dto.comment.response.get_commentreply_response import GetCommentReplyResponse
from dto.comment.response.update_status_comment_reply_response import UpdateStatusCommentReplyResponse
from models.post_model import CommentReact
from typing import List, Optional

class ICommentService(ABC):
    @abstractmethod
    async def add(self, post_req: AddCommentRequest, user_id: str) -> AddCommentResponse:
        pass

    @abstractmethod
    async def update_react(self, post_id: str, comment_id: str, react: CommentReact) -> Optional[dict]:
        pass

    @abstractmethod
    async def find_by_id(self, post_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def add_comment_reply(self, comment_req: AddCommentReplyRequest) -> Optional[AddCommentReplyResponse]:
        pass

    @abstractmethod
    async def get_comment_reply(self, req: GetCommentReplyRequest) -> Optional[GetCommentReplyResponse]:
        pass

    @abstractmethod
    async def update_status_comment_reply(self, req: UpdateStatusCommentReplyRequest) -> List[UpdateStatusCommentReplyResponse]:
        pass

    @abstractmethod
    async def update_react_comment_reply(self, post_id: str, comment_id: str, react: CommentReact) -> Optional[dict]:
        pass
