from datetime import datetime, timedelta, timezone
from typing import List, Optional
from dto.post.request.get_my_post_request import GetMyPostRequest
from dto.post.request.get_post_by_email_request import GetPostByEmailRequest
from dto.post.request.get_post_suggest_request import GetPostSuggestRequest
from dto.post.response.get_post_by_email_response import GetPostByEmailResponse
from dto.post.response.get_post_suggest_response import GetPostSuggestResponse
from dto.statistic.request.get_post_of_day_request import GetPostOfDayRequest
from dto.statistic.request.get_top_interacted_post_request import GetTopInteractedPostRequest
from dto.statistic.response.get_post_of_day_response import GetPostOfDayResponse
from dto.statistic.response.get_top_interacted_post_response import GetTopInteractedPostReponse, TopPost
from repositories.account_repository import AccountRepository
from repositories.commentreply_repository import CommentReplyRepository
from services.interfaces.post_service_interface import IPostService
from repositories.post_repository import PostRepository
from dto.post.request.add_post_request import AddPostRequest
from dto.post.response.add_post_response import AddPostResponse
from dto.post.request.get_post_request import GetPostRequest
from dto.post.response.get_post_response import GetPostResponse
from dto.post.request.update_post_request import UpdatePostRequest
from dto.post.response.update_post_response import UpdatePostResponse
from dto.post.request.get_all_post_request import GetAllPostRequest
from dto.post.response.get_all_post_response import GetAllPostResponse 
from dto.post.request.delete_post_request import DeletePostRequest
from dto.post.response.delete_post_response import DeletePostResponse
from models.post_model import Post, React
from models.base_model import bson_to_dict

from core.database import db 
from repositories.interaction_repository import InteractionRepository
from core.redis import (
    get_cached_feed, cache_feed,
    get_viewed_posts, mark_post_viewed, invalidate_feed_cache, reset_viewed_posts
)
from services.other.file_service import FileService
MAX_TAKE = 20

from middleware.moderation_middleware import get_moderation_middleware
from exceptions.moderation_exception import ModerationException
from dto.ai.request.moderate_content_request import ModerateContentRequest


class PostServiceImpl(IPostService):

    async def add(self, post_req: AddPostRequest) -> Optional[AddPostResponse]:
        title = post_req.title.strip() if post_req.title else ""
        content = post_req.content.strip() if post_req.content else ""
        
        # if not title and not content:
        #     return AddPostResponse(success=False, message="Bài đăng phải có tiêu đề hoặc nội dung")
        
        # ==================== AI MODERATION ====================
        full_text = f"{title}\n{content}".strip()
        
        moderation = get_moderation_middleware()
        mod_result = await moderation.check_only(
            content=full_text,
            content_type="post"
        )

        if not mod_result.approved:
            raise ModerationException(
                reason=mod_result.reason,
                violated_categories=mod_result.violated_categories,
                scores=mod_result.scores.model_dump() if mod_result.scores else {},
                confidence=mod_result.confidence
            )
        
        # Chuẩn bị data lưu DB
        post_dict = post_req.model_dump()
        
        # Thêm kết quả moderation vào document
        post_dict["ai_moderation"] = {
            "approved": True,
            "scores": mod_result.scores.model_dump() if mod_result.scores else {},
            "confidence": mod_result.confidence,
            "moderated_at": datetime.now(timezone.utc).isoformat(),
            "model": "llama3.1:8b"  # Đổi thành model bạn đang dùng
        }
        
        # Insert vào DB
        new_post = await PostRepository.insert(post_dict)
        
        if new_post:
            return AddPostResponse(success=True, message="Completed")
        else:
            return AddPostResponse(success=False, message="Failed to add post")


    # async def get_all(self, req: GetAllPostRequest) -> Optional[GetAllPostResponse]:
    #     uid = req.email
    #     dic_acc = await AccountRepository.find_by_email(uid)
    #     # 1. Cache
    #     # cached = await get_cached_feed(uid)
    #     # if cached:
    #     #     return GetAllPostResponse(post_list=[Post(**d) for d in cached])

    #     # 2. Đã xem
    #     viewed = await get_viewed_posts(uid)

    #     # 3. Follow & department
    #     me = await db["account"].find_one(
    #         {"email": uid},
    #         {"userInfo.followed": 1, "userInfo.department": 1}
    #     )
    #     followed = me.get("userInfo", {}).get("followed", [])
    #     user_dept = me.get("userInfo", {}).get("department")

    #     # 4. Interacted
    #     interacted = await InteractionRepository(db).get_interacted_emails(uid)
    #     interacted = list(interacted - set(followed))
        
    #     # 5. Lấy hết bài chưa xem (không giới hạn)
    #     new_docs = await PostRepository.get_ranked_posts(
    #         email=uid,
    #         followed=followed,
    #         interacted=interacted,
    #         user_dept=user_dept,
    #         exclude_ids=list(viewed),
    #         limit=None,
    #         myAccount=dic_acc
    #     )

    #     # 6. Refill bài đã xem đến MAX_TAKE (kể cả 0)
    #     needed = 300 - len(new_docs)          # có thể = 0
    #     old_docs = []
    #     if needed > 0:       
    #         total_valid = await db["post"].count_documents({"visibility": "public", "status": "active"})
    #         old_docs = await PostRepository.get_ranked_posts(
    #             email=uid,
    #             followed=followed,
    #             interacted=interacted,
    #             user_dept=user_dept,
    #             exclude_ids=[],
    #             limit=needed,
    #             myAccount=dic_acc
    #         )
    #         seen_ids = {str(d["_id"]) for d in new_docs}
    #         old_docs = [d for d in old_docs if str(d["_id"]) not in seen_ids]

    #     # 7. Ghép & giữ thứ tự ưu tiên
    #     docs = (new_docs + old_docs)[:MAX_TAKE]

    #     # 8. Cache & mark viewed
    #     serializable = [bson_to_dict(d) for d in docs]
    #     await cache_feed(uid, serializable)
    #     for d in docs:
    #         await mark_post_viewed(uid, str(d["_id"]))
    #     return GetAllPostResponse(post_list=[Post(**d) for d in docs])
    # async def get_all(self, req: GetAllPostRequest) -> Optional[GetAllPostResponse]:
    #     uid = req.email
    #     dic_acc = await AccountRepository.find_by_email(uid)

    #     # 1. Cache - TẮT KHI DEV
    #     # cached = await get_cached_feed(uid)
    #     # if cached:
    #     #     return GetAllPostResponse(post_list=[Post(**d) for d in cached])

    #     # 2. Đã xem
    #     viewed = await get_viewed_posts(uid)

    #     # 3. Follow & department
    #     me = await db["account"].find_one(
    #         {"email": uid},
    #         {"userInfo.followed": 1, "userInfo.department": 1}
    #     )
    #     followed = me.get("userInfo", {}).get("followed", [])
    #     user_dept = me.get("userInfo", {}).get("department")

    #     # 4. Interacted
    #     interacted = await InteractionRepository(db).get_interacted_emails(uid)
    #     interacted = list(interacted - set(followed))

    #     # 5. Lấy bài chưa xem, giới hạn MAX_TAKE
    #     new_docs = await PostRepository.get_ranked_posts(
    #         email=uid,
    #         followed=followed,
    #         interacted=interacted,
    #         user_dept=user_dept,
    #         exclude_ids=list(viewed),   # exclude đúng bài đã xem
    #         limit=MAX_TAKE,
    #         myAccount=dic_acc
    #     )

    #     # 6. Refill bài đã xem nếu chưa đủ MAX_TAKE
    #     needed = MAX_TAKE - len(new_docs)
    #     old_docs = []
    #     if needed > 0 and len(viewed) > 0:
    #         seen_new_ids = {str(d["_id"]) for d in new_docs}
    #         old_docs = await PostRepository.get_ranked_posts(
    #             email=uid,
    #             followed=followed,
    #             interacted=interacted,
    #             user_dept=user_dept,
    #             exclude_ids=list(seen_new_ids),  # chỉ exclude bài vừa lấy, không exclude viewed
    #             limit=needed,
    #             myAccount=dic_acc
    #         )

    #     # 7. Ghép & giữ thứ tự ưu tiên
    #     docs = (new_docs + old_docs)[:MAX_TAKE]

    #     # 8. Cache & mark viewed - TẮT KHI DEV
    #     # serializable = [bson_to_dict(d) for d in docs]
    #     # await cache_feed(uid, serializable)
    #     # for d in docs:
    #     #     await mark_post_viewed(uid, str(d["_id"]))

    #     def normalize_doc(d: dict) -> dict:
    #         d = dict(d)
    #         if "_id" in d and not isinstance(d["_id"], str):
    #             d["_id"] = str(d["_id"])
    #         return d

    #     return GetAllPostResponse(post_list=[Post(**normalize_doc(d)) for d in docs])
    async def get_all(self, req: GetAllPostRequest) -> Optional[GetAllPostResponse]:
        uid = req.email
        dic_acc = await AccountRepository.find_by_email(uid)

        # 1. Lấy danh sách bài đã xem từ Redis
        viewed = await get_viewed_posts(uid)

        # 2. Follow & department
        me = await db["account"].find_one(
            {"email": uid},
            {"userInfo.followed": 1, "userInfo.department": 1}
        )
        followed = me.get("userInfo", {}).get("followed", [])
        user_dept = me.get("userInfo", {}).get("department")

        # 3. Interacted
        interacted = await InteractionRepository(db).get_interacted_emails(uid)
        interacted = list(interacted - set(followed))

        # 4. Lấy bài chưa xem, giới hạn MAX_TAKE
        new_docs = await PostRepository.get_ranked_posts(
            email=uid,
            followed=followed,
            interacted=interacted,
            user_dept=user_dept,
            exclude_ids=list(viewed),
            limit=MAX_TAKE,
            myAccount=dic_acc
        )

        # 5. Refill bằng bài đã xem nếu không còn đủ bài mới
        docs = new_docs
        if len(new_docs) < MAX_TAKE:
            needed = MAX_TAKE - len(new_docs)
            seen_new_ids = {str(d["_id"]) for d in new_docs}

            # Reset viewed vì đã hết bài mới, bắt đầu chu kỳ mới
            await reset_viewed_posts(uid)

            old_docs = await PostRepository.get_ranked_posts(
                email=uid,
                followed=followed,
                interacted=interacted,
                user_dept=user_dept,
                exclude_ids=list(seen_new_ids),
                limit=needed,
                myAccount=dic_acc
            )
            docs = (new_docs + old_docs)[:MAX_TAKE]

        # 6. Đánh dấu các bài vừa trả về là đã xem
        for d in docs:
            await mark_post_viewed(uid, str(d["_id"]))

        def normalize_doc(d: dict) -> dict:
            d = dict(d)
            if "_id" in d and not isinstance(d["_id"], str):
                d["_id"] = str(d["_id"])
            return d

        return GetAllPostResponse(post_list=[Post(**normalize_doc(d)) for d in docs])


    async def get_by_id(self, post_id: GetPostRequest) -> Optional[GetPostResponse]:
        post = await PostRepository.find_by_id(post_id.id)
        if post:
            return GetPostResponse(post=Post(**bson_to_dict(post))) 
        return None


    async def update(self, post_req: UpdatePostRequest) -> Optional[UpdatePostResponse]:
        # Nếu không đổi title/content -> update bình thường
        if post_req.title is None and post_req.content is None:
            updated_post = await PostRepository.update(post_req.model_dump(exclude_none=True))
            if updated_post:
                return UpdatePostResponse(post=Post(**bson_to_dict(updated_post)))
            return None
        
        # ==================== AI REMODERATION ====================
        # Lấy post cũ để biết giá trị hiện tại nếu chỉ update 1 field
        existing = await PostRepository.find_by_id(post_req.id)
        if not existing:
            return None  # Hoặc raise HTTPException(404) tùy bạn
        
        current_title = existing.get("title", "")
        current_content = existing.get("content", "")
        
        new_title = post_req.title if post_req.title is not None else current_title
        new_content = post_req.content if post_req.content is not None else current_content
        
        full_text = f"{new_title}\n{new_content}".strip()
        
        moderation = get_moderation_middleware()
        mod_result = await moderation.check_only(
            content=full_text,
            content_type="post"
        )
        
        if not mod_result.approved:
            raise ModerationException(
                reason=mod_result.reason,
                violated_categories=mod_result.violated_categories,
                scores=mod_result.scores.model_dump() if mod_result.scores else {},
                confidence=mod_result.confidence
            )
        
        # Chuẩn bị update data
        update_data = post_req.model_dump(exclude_none=True)
        
        # Cập nhật ai_moderation mới
        update_data["ai_moderation"] = {
            "approved": True,
            "scores": mod_result.scores.model_dump() if mod_result.scores else {},
            "confidence": mod_result.confidence,
            "moderated_at": datetime.now(timezone.utc).isoformat(),
            "model": "llama3.1:8b"
        }
        
        updated_post = await PostRepository.update(update_data)
        
        if updated_post:
            return UpdatePostResponse(post=Post(**bson_to_dict(updated_post)))
        return None


    async def delete(self, post_id: DeletePostRequest) -> Optional[DeletePostResponse]:
        rs = await PostRepository.delete(post_id.id)
        if rs:
            return DeletePostResponse(success=True, message="Deleted")
        else:
            return DeletePostResponse(success=False, message="Failed to delete post")
        
    async def update_comment_status(self, post_id: str, comment_id: str, status_comment: str):
        # updated_post = await PostRepository.update_comment_status(post_id, comment_id, status_comment)
        # if updated_post:
        #     return UpdatePostResponse(post=Post(**bson_to_dict(updated_post)))
        # return None

        updated_post = await PostRepository.update_comment_status(post_id, comment_id, status_comment)
        if not updated_post:
            return None
        
        await CommentReplyRepository.update_comment_status_by_parent(
            post_id=post_id,
            parent_comment_id=comment_id,
            status=status_comment
        )
        return UpdatePostResponse(post=Post(**bson_to_dict(updated_post)))
    

    async def find_by_id(self, post_id: str):
        """
        Trả về Post model trực tiếp, dùng cho toggle_react
        """
        post_data = await PostRepository.find_by_id(post_id)
        if post_data:
            return Post(**bson_to_dict(post_data))
        return None
    
    async def update_react(self, post_id: str, react: React) -> Post | None:
        """
        Gọi repository để cập nhật field 'react' của bài viết.
        """
        updated_post = await PostRepository.update_react(post_id, react)
        if updated_post:
            return Post(**bson_to_dict(updated_post))
        return None
    
    async def get_by_email(self, req: GetPostByEmailRequest) -> GetPostByEmailResponse:
        posts_data = await PostRepository.find_by_email(req.email, req.ownerEmail)
        posts = [Post(**bson_to_dict(p)) for p in posts_data]
        return GetPostByEmailResponse(post_list=posts)
    
    async def get_my_post(self, post_list: GetMyPostRequest) -> GetAllPostResponse:
        dic_posts = await PostRepository.find_by_email(post_list.email)
        posts: list[Post] = []
        if len(dic_posts) > 0:
            for dic in dic_posts:
                post: Post = Post(**bson_to_dict(dic))
                posts.append(post)
        return GetAllPostResponse(post_list=posts)
    
    async def get_post_of_day(self, req: GetPostOfDayRequest) -> GetPostOfDayResponse:
        rs = await PostRepository.get_post_of_day()
        return GetPostOfDayResponse(success=True, data=rs)
    
    async def get_top_interacted_posts_in_week(self, req: GetTopInteractedPostRequest) -> GetTopInteractedPostReponse:
        post_dic = await PostRepository.get_top_interacted_posts_in_week(10)
        data: List[TopPost] = []
        for dic in post_dic:
            post: TopPost = TopPost(**bson_to_dict(dic))
            data.append(post)
        return GetTopInteractedPostReponse(success=True, data=data)
    
    async def get_post_suggest(self, req: GetPostSuggestRequest) -> GetPostSuggestResponse:
        post_dic = await PostRepository.get_post_suggest(req.email)
        pl: List[Post] = []
        if len(post_dic) > 0:
            for dic in post_dic:
                post: Post = Post(**bson_to_dict(dic))
                pl.append(post)
        rs = GetPostSuggestResponse(list_post=pl)
        return rs

    async def get_post_hidden_by_email(self, req: GetMyPostRequest) -> GetAllPostResponse:
        dic = await PostRepository.get_post_hidden_by_email(req.email)
        rs = GetAllPostResponse(post_list=[Post(**bson_to_dict(p)) for p in dic])
        for p in rs.post_list:
            if p.thumbnails:
                p.thumbnails_url = [FileService.get_file_url(file_id) for file_id in p.thumbnails]
            else:
                p.thumbnails_url = []
            
            if p.comments:
                p.comments = [
                    c for c in p.comments if c.statusComment != "hidden"
                ]
        return rs




