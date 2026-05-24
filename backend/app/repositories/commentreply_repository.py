import re

from core.database import db
from bson import ObjectId
from datetime import datetime, timezone
import uuid
from models.post_model import Comment, CommentReact

class CommentReplyRepository:
    collection = db["commentreply"]

    @staticmethod
    async def insert(data: dict) -> dict | None:
        rs = await CommentReplyRepository.collection.insert_one(data)
        if rs: print(rs)
        new_rs = await CommentReplyRepository.collection.find_one({"_id": rs.inserted_id})
        return new_rs
    
    @staticmethod
    async def find_by_path(postid: str, parentId: str) -> list[dict]:
        pattern = f"(^|;){re.escape(parentId)}(;|$)"
        cursor = CommentReplyRepository.collection.find({
            "postId": postid,
            "path": {"$regex": pattern}
        })
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def find_by_id(commentId: str) -> dict | None:
        return await CommentReplyRepository.collection.find_one({"commentId": commentId})
    
    @staticmethod
    async def update_comment_status(postId: str, commentId: str, path: str, status: str):
        print("ahihihihihihi")
        print("postId:", postId)
        print("commentId:", commentId)
        
        pattern = f"(^|;){re.escape(commentId)}(;|$)"
        print("pattern:", pattern)
        result = await CommentReplyRepository.collection.update_many(
            {
                "postId": postId,
                "path": {"$regex": pattern}
            },
            {
                "$set": {"status": status}
            }
        )

        if result.modified_count == 0:
            return None
        
        updated_comments = await CommentReplyRepository.collection.find({
            "postId": postId,
            "path": {"$regex": pattern}
        }).to_list(length=None)

        return updated_comments
    
    @staticmethod
    async def update_comment_status_by_parent(post_id: str, parent_comment_id: str, status: str):
        pattern = f"(^|;){re.escape(parent_comment_id)}(;|$)"

        result = await CommentReplyRepository.collection.update_many(
            {
                "postId": post_id,
                "path": {"$regex": pattern}
            },
            {
                "$set": {"status": status}
            }
        )

        return result.modified_count
    
    @staticmethod
    async def update_comment_reply_react(post_id: str, comment_id: str, react: CommentReact) -> dict | None:
        react_dict = react.dict()

        result = await CommentReplyRepository.collection.update_one(
            {"postId": post_id, "commentId": comment_id},
            {"$set": {"react": react_dict}}
        )

        if result.modified_count == 0:
            return None
        return await CommentReplyRepository.find_by_id(comment_id)



    # @staticmethod
    # async def update_comment_react(post_id: str, comment_id: str, react: CommentReact) -> dict | None:
    #     react_dict = react.dict()

    #     result = await CommentRepository.collection.update_one(
    #         {"_id": ObjectId(post_id), "comments.commentId": comment_id},
    #         {"$set": {"comments.$.reacts": react_dict}}
    #     )

    #     if result.modified_count == 0:
    #         return None
    #     return await CommentRepository.find_by_id(post_id)

    # @staticmethod
    # async def find_by_id(post_id: str) -> dict | None:
    #     return await CommentRepository.collection.find_one({"_id": ObjectId(post_id)})
    
    # @staticmethod
    # async def get_comment_info(post_id: str, comment_id: str):
    #     post = await PostRepository.collection.find_one(
    #         {"_id": ObjectId(post_id), "comments.commentId": comment_id},
    #         {"comments.$": 1}  # chỉ lấy đúng comment đó
    #     )

    #     if not post or "comments" not in post:
    #         return None

    #     comment = post["comments"][0]

    #     return {
    #         "commentBy": comment.get("commentBy"),
    #         "content": comment.get("content")
    #     }
