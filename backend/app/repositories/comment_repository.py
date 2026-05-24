from typing import List

from core.database import db
from bson import ObjectId
from datetime import datetime, timezone
import uuid
from models.post_model import Comment, CommentReact
from repositories.post_repository import PostRepository

class CommentRepository:
    collection = db["post"]

    @staticmethod
    async def add_comment(post_id: str, user_id: str, comment_data: dict, thumb: List[str]):
        new_comment = Comment(
            commentId=str(uuid.uuid4()),
            commentBy=user_id,
            content=comment_data["content"],
            reacts=CommentReact(),
            createdAt=datetime.now(timezone.utc),
            statusComment="active",
            thumbnails=thumb
        ).dict()

        result = await CommentRepository.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": new_comment}}
        )

        if result.modified_count == 0:
            return None
        return new_comment

    @staticmethod
    async def update_comment_react(post_id: str, comment_id: str, react: CommentReact) -> dict | None:
        react_dict = react.dict()

        result = await CommentRepository.collection.update_one(
            {"_id": ObjectId(post_id), "comments.commentId": comment_id},
            {"$set": {"comments.$.reacts": react_dict}}
        )

        if result.modified_count == 0:
            return None
        return await CommentRepository.find_by_id(post_id)

    @staticmethod
    async def find_by_id(post_id: str) -> dict | None:
        return await CommentRepository.collection.find_one({"_id": ObjectId(post_id)})
    
    @staticmethod
    async def get_comment_info(post_id: str, comment_id: str):
        post = await PostRepository.collection.find_one(
            {"_id": ObjectId(post_id), "comments.commentId": comment_id},
            {"comments.$": 1}  # chỉ lấy đúng comment đó
        )

        if not post or "comments" not in post:
            return None

        comment = post["comments"][0]

        return {
            "commentBy": comment.get("commentBy"),
            "content": comment.get("content")
        }
