from fastapi import APIRouter, Depends, HTTPException
from typing import List
from dto.comment.request.add_comment_request import AddCommentRequest
from dto.comment.request.add_commentreply_request import AddCommentReplyRequest
from dto.comment.request.get_commentreply_request import GetCommentReplyRequest
from dto.comment.request.update_status_comment_reply_request import UpdateStatusCommentReplyRequest
from dto.comment.response.add_comment_response import AddCommentResponse
from dto.comment.response.add_commentreply_response import AddCommentReplyResponse
from dto.comment.response.get_commentreply_response import GetCommentReplyResponse
from dto.comment.response.update_status_comment_reply_response import UpdateStatusCommentReplyResponse
from exceptions.moderation_exception import ModerationException
from repositories.commentreply_repository import CommentReplyRepository
from services.interfaces.comment_service_interface import ICommentService
from repositories.comment_repository import CommentRepository
from dto.comment.response.update_comment_react_response import UpdateCommentReactResponse
from models.post_model import React
from models.post_model import CommentReact
from services.interfaces.post_service_interface import IPostService
from services.interfaces.comment_service_interface import ICommentService
from core.dependency import get_comment_service
from utils.security import get_current_user


router = APIRouter()

@router.post("/add_comment", response_model=AddCommentResponse)
async def add_comment(
    comment: AddCommentRequest,
    current_user: dict = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    try:
        user_id = current_user.get("sub")
        return await service.add(comment, user_id)
    except ModerationException as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Nội dung không được phép bình luận",
                "reason": e.reason,
                "violated_categories": e.violated_categories,
                "scores": e.scores,
                "confidence": e.confidence,
                "suggestion": "Vui lòng chỉnh sửa nội dung theo hướng dẫn và thử lại."
            }
        )

@router.put("/{post_id}/comments/{comment_id}/react/{react_type}", response_model=UpdateCommentReactResponse)
async def toggle_comment_react(
    post_id: str,
    comment_id: str,
    react_type: str,
    current_user: dict = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    user_email = current_user["sub"]
    valid_types = ["love", "like", "haha", "wow", "sad", "angry"]

    if react_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid react type")

    post = await service.find_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = next((c for c in post.get("comments", []) if c["commentId"] == comment_id), None)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    react = CommentReact(**comment.get("reacts", {}))
    current_list = getattr(react, react_type)
    if user_email in current_list:
        current_list.remove(user_email)
    else:
        for r in valid_types:
            if r != react_type:
                other_list = getattr(react, r)
                if user_email in other_list:
                    other_list.remove(user_email)
        current_list.append(user_email)

    setattr(react, react_type, current_list)

    await service.update_react(post_id, comment_id, react)

    return UpdateCommentReactResponse(message="Comment reaction updated", react=react)

@router.post("/add_comment_reply", response_model=AddCommentReplyResponse)
async def add_comment(
    request: AddCommentReplyRequest,
    current_user: dict = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    try:
        request.commentBy = current_user.get("sub")
        return await service.add_comment_reply(request)
    except ModerationException as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Nội dung không được phép bình luận",
                "reason": e.reason,
                "violated_categories": e.violated_categories,
                "scores": e.scores,
                "confidence": e.confidence,
                "suggestion": "Vui lòng chỉnh sửa nội dung theo hướng dẫn và thử lại."
            }
        )

@router.post("/get_comment_reply", response_model=GetCommentReplyResponse)
async def get_comment_reply(
    request: GetCommentReplyRequest,
    current_user: dict = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    return await service.get_comment_reply(req=request)

@router.put("/update_status_comment_reply", response_model=List[UpdateStatusCommentReplyResponse])
async def update_status_comment_reply(
    req: UpdateStatusCommentReplyRequest,
    # current_user: dict = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    updated = await service.update_status_comment_reply(req)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return updated

@router.put("/{post_id}/comment_reply/{comment_id}/react/{react_type}", response_model=UpdateCommentReactResponse)
async def toggle_comment_react(
    post_id: str,
    comment_id: str,
    react_type: str,
    current_user: dict = Depends(get_current_user),
    service: ICommentService = Depends(get_comment_service)
):
    user_email = current_user["sub"]
    valid_types = ["love", "like", "haha", "wow", "sad", "angry"]

    if react_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid react type")

    post = await service.find_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = await CommentReplyRepository.find_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    react = CommentReact(**comment.get("react", {}))
    current_list = getattr(react, react_type)
    if user_email in current_list:
        current_list.remove(user_email)
    else:
        for r in valid_types:
            if r != react_type:
                other_list = getattr(react, r)
                if user_email in other_list:
                    other_list.remove(user_email)
        current_list.append(user_email)

    setattr(react, react_type, current_list)

    await service.update_react_comment_reply(post_id, comment_id, react)

    return UpdateCommentReactResponse(message="Comment reaction updated", react=react)




