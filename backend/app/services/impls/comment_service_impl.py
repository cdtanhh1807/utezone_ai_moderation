from datetime import datetime, timezone
import uuid
from dto.comment.request.add_comment_request import AddCommentRequest
from dto.comment.request.add_commentreply_request import AddCommentReplyRequest
from dto.comment.request.get_commentreply_request import GetCommentReplyRequest
from dto.comment.request.update_status_comment_reply_request import UpdateStatusCommentReplyRequest
from dto.comment.response.add_comment_response import AddCommentResponse
from dto.comment.response.add_commentreply_response import AddCommentReplyResponse
from dto.comment.response.get_commentreply_response import GetCommentReplyResponse
from dto.comment.response.update_status_comment_reply_response import UpdateStatusCommentReplyResponse
from exceptions.moderation_exception import ModerationException
from middleware.moderation_middleware import get_moderation_middleware
from models.account_model import Account
from models.announce_model import Announce
from models.commentreply_model import CommentReply
from repositories.account_repository import AccountRepository
from repositories.announce_repository import AnnounceRepository
from repositories.commentreply_repository import CommentReplyRepository
from repositories.post_repository import PostRepository
from services.interfaces.comment_service_interface import ICommentService
from repositories.comment_repository import CommentRepository
from models.post_model import CommentReact, Post
from typing import List, Optional
from models.base_model import bson_to_dict
from services.other.file_service import FileService

class CommentServiceImpl(ICommentService):

    async def add(self, post_req: AddCommentRequest, user_id: str) -> AddCommentResponse:
        content = post_req.content.strip() if post_req.content else ""
        moderation = get_moderation_middleware()
        mod_result = await moderation.check_only(
            content=content,
            content_type="comment"
        )
        
        if not mod_result.approved:
            raise ModerationException(
                reason=mod_result.reason,
                violated_categories=mod_result.violated_categories,
                scores=mod_result.scores.model_dump() if mod_result.scores else {},
                confidence=mod_result.confidence
            )
        
        new_comment = await CommentRepository.add_comment(
            post_id=post_req.postId,
            user_id=user_id,
            comment_data=post_req.model_dump(),
            thumb=post_req.thumbnails
        )
        
        if new_comment:
            dic_post = await PostRepository.find_by_id(post_req.postId)
            post: Post = Post(**bson_to_dict(dic_post))
            dic_acc = await AccountRepository.find_by_email(post.createdBy)
            acc: Account = Account(**bson_to_dict(dic_acc))
            dic_acc_tp = await AccountRepository.find_by_email(user_id)
            acc_tp: Account = Account(**bson_to_dict(dic_acc_tp))
            contentAnnounce: str = str(acc_tp.userInfo.fullName) + " đã bình luận bài viết của bạn"
            announce = Announce(senderEmail=user_id, receiverEmail=post.createdBy, type="comment", contentAnnounce=contentAnnounce,
                                 isRead=False, createdAt=datetime.now(), contentId=new_comment.get("commentId"),
                                 contentParentId=str(post.id), content=new_comment.get("content"))
            dic_announce_insert = await AnnounceRepository.insert(announce.model_dump())
            if dic_announce_insert:
                return AddCommentResponse(
                    success=True,
                    message="Comment added successfully.",
                    comment=new_comment
                )
        else:
            return AddCommentResponse(success=False, message="Post not found.")
        
    # async def add(self, post_req: AddCommentRequest, user_id: str) -> AddCommentResponse:
    #     new_comment = await CommentRepository.add_comment(
    #         post_id=post_req.postId,
    #         user_id=user_id,
    #         comment_data=post_req.model_dump(),
    #         thumb=post_req.thumbnails
    #     )

    #     # if new_comment:
    #     #     return AddCommentResponse(
    #     #         success=True,
    #     #         message="Comment added successfully.",
    #     #         comment=new_comment
    #     #     )
    #     if new_comment:
    #         dic_post = await PostRepository.find_by_id(post_req.postId)
    #         post: Post = Post(**bson_to_dict(dic_post))
    #         dic_acc = await AccountRepository.find_by_email(post.createdBy)
    #         acc: Account = Account(**bson_to_dict(dic_acc))
    #         dic_acc_tp = await AccountRepository.find_by_email(user_id)
    #         acc_tp: Account = Account(**bson_to_dict(dic_acc_tp))
    #         contentAnnounce: str = str(acc_tp.userInfo.fullName) + " đã bình luận bài viết của bạn"
    #         announce = Announce(senderEmail=user_id, receiverEmail=post.createdBy, type="comment", contentAnnounce=contentAnnounce,
    #                              isRead=False, createdAt=datetime.now(timezone.utc), contentId=new_comment.get("commentId"),
    #                              contentParentId=str(post.id), content=new_comment.get("content"))
    #         dic_announce_insert = await AnnounceRepository.insert(announce.model_dump())
    #         if dic_announce_insert:
    #             return AddCommentResponse(
    #                 success=True,
    #                 message="Comment added successfully.",
    #                 comment=new_comment
    #             )
    #     else:
    #         return AddCommentResponse(success=False, message="Post not found.")

    async def update_react(self, post_id: str, comment_id: str, react: CommentReact) -> Optional[dict]:
        updated_post = await CommentRepository.update_comment_react(post_id, comment_id, react)
        return bson_to_dict(updated_post) if updated_post else None

    async def find_by_id(self, post_id: str) -> Optional[dict]:
        return await CommentRepository.find_by_id(post_id)
    
    async def add_comment_reply(self, comment_req: AddCommentReplyRequest) -> Optional[AddCommentReplyResponse]:
        # Kiểm duyệt nội dung text
        content = comment_req.content.strip() if comment_req.content else ""
        if content:
            moderation = get_moderation_middleware()
            mod_result = await moderation.check_only(
                content=content,
                content_type="comment"  # Dùng chung loại comment
            )
            if not mod_result.approved:
                raise ModerationException(
                    reason=mod_result.reason,
                    violated_categories=mod_result.violated_categories,
                    scores=mod_result.scores.model_dump() if mod_result.scores else {},
                    confidence=mod_result.confidence
                )
        
        # Tạo comment reply (giữ nguyên logic cũ)
        commentId = str(uuid.uuid4())
        path = ""
        if not comment_req.path:
            path = comment_req.parentId + ";" + commentId
        else:
            path = comment_req.path + ";" + commentId

        commentReply: CommentReply = CommentReply(
            commentId=commentId,
            commentBy=comment_req.commentBy,
            postId=comment_req.postId,
            path=path,
            content=comment_req.content,
            createdAt=datetime.now(timezone.utc),
            status="active",
            thumbnails=comment_req.thumbnails
        )

        rs = await CommentReplyRepository.insert(commentReply.model_dump())
        if rs:
            return AddCommentReplyResponse(commentReply=CommentReply(**bson_to_dict(rs)))
        return None
    # async def add_comment_reply(self, comment_req: AddCommentReplyRequest) -> Optional[AddCommentReplyResponse]:
    #     commentId=str(uuid.uuid4())
    #     path = ""
    #     if not comment_req.path: path = comment_req.parentId + ";" + commentId
    #     else: path = comment_req.path + ";" + commentId

    #     commentReply: CommentReply = CommentReply(commentId=commentId, commentBy=comment_req.commentBy, 
    #                                               postId=comment_req.postId, path=path, content=comment_req.content,
    #                                                 createdAt=datetime.now(timezone.utc), status="active", thumbnails=comment_req.thumbnails)

    #     rs = await CommentReplyRepository.insert(commentReply.model_dump())
    #     if rs: return AddCommentReplyResponse(commentReply=CommentReply(**bson_to_dict(rs)))
    #     return None
    
    async def get_comment_reply(self, req: GetCommentReplyRequest) -> Optional[GetCommentReplyResponse]:
        dic = await CommentReplyRepository.find_by_path(req.postId, req.parentId)
        rs = GetCommentReplyResponse(commentReplys=[CommentReply(**c) for c in dic if c.get("status") == "active"])
        for c in rs.commentReplys:
            if c.thumbnails:
                c.thumbnails_url = [FileService.get_file_url(file_id) for file_id in c.thumbnails]
            else:
                c.thumbnails_url = []
        return rs
    
    async def update_status_comment_reply(self, req: UpdateStatusCommentReplyRequest) -> List[UpdateStatusCommentReplyResponse]:
        updated_cmts = await CommentReplyRepository.update_comment_status(
            req.postId, req.commentId, req.path, req.status
        )

        if updated_cmts:
            return [
                UpdateStatusCommentReplyResponse(
                    commentReply=CommentReply(**bson_to_dict(cmt))
                )
                for cmt in updated_cmts
            ]

        return []
    
    async def update_react_comment_reply(self, post_id: str, comment_id: str, react: CommentReact) -> Optional[dict]:
        updated_comment = await CommentReplyRepository.update_comment_reply_react(post_id, comment_id, react)
        return bson_to_dict(updated_comment) if updated_comment else None

