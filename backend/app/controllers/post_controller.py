from typing import List
from fastapi import APIRouter, Depends, HTTPException
from core.redis import get_viewed_posts
from dto.comment.response.get_commentreply_response import GetCommentReplyResponse
from dto.post.request.add_post_request import AddPostRequest
from dto.post.request.get_my_post_request import GetMyPostRequest
from dto.post.request.get_post_by_email_request import GetPostByEmailRequest
from dto.post.request.get_post_suggest_request import GetPostSuggestRequest
from dto.post.request.share_post_request import SharePostRequest
from dto.post.request.update_comment_status_request import UpdateCommentStatusRequest
from dto.post.response.add_post_response import AddPostResponse
from dto.post.request.get_post_request import GetPostRequest
from dto.post.response.get_post_by_email_response import GetPostByEmailResponse
from dto.post.response.get_post_response import GetPostResponse
from dto.post.request.update_post_request import UpdatePostRequest
from dto.post.response.get_post_suggest_response import GetPostSuggestResponse
from dto.post.response.update_post_react_response import UpdatePostReactResponse
from dto.post.response.update_post_response import UpdatePostResponse
from dto.post.request.get_all_post_request import GetAllPostRequest
from dto.post.response.get_all_post_response import GetAllPostResponse 
from dto.post.request.delete_post_request import DeletePostRequest
from dto.post.response.delete_post_response import DeletePostResponse
from dto.statistic.request.get_post_of_day_request import GetPostOfDayRequest
from dto.statistic.request.get_top_interacted_post_request import GetTopInteractedPostRequest
from dto.statistic.response.get_post_of_day_response import GetPostOfDayResponse
from dto.statistic.response.get_top_interacted_post_response import GetTopInteractedPostReponse
from models.post_model import React
from services.interfaces.post_service_interface import IPostService
from core.dependency import get_post_service
from services.other.file_service import FileService
from utils.security import get_current_user


from exceptions.moderation_exception import ModerationException

router = APIRouter()

@router.post("/add_post", response_model=AddPostResponse)
async def add_post(
    post: AddPostRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    # post.createdBy = current_user["sub"]
    # return await service.add(post)
    try:
        post.createdBy = current_user["sub"]
        return await service.add(post)
    except ModerationException as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Nội dung không được phép đăng",
                "reason": e.reason,
                "violated_categories": e.violated_categories,
                "scores": e.scores,
                "confidence": e.confidence,
                "suggestion": "Vui lòng chỉnh sửa nội dung theo hướng dẫn và thử lại."
            }
        )


@router.get("/get_all_post", response_model=GetAllPostResponse)
async def list_posts(
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    req = GetAllPostRequest(email=current_user["sub"])
    rs= await service.get_all(req)

    for p in rs.post_list:
        if p.status == "off":
            continue
        if p.comments:
            p.comments = [
                c for c in p.comments 
                if c.statusComment != "hidden"
            ]
            for tb in p.comments:
                if tb.thumbnails: tb.thumbnails_url = [FileService.get_file_url(file_id) for file_id in tb.thumbnails]
        if p.thumbnails:
            p.thumbnails_url = [FileService.get_file_url(file_id) for file_id in p.thumbnails]
        else:
            p.thumbnails_url = []
    return rs

@router.get("/get_post/{post_id}", response_model=GetPostResponse)
async def get_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    id = GetPostRequest(id=post_id)
    post = await service.get_by_id(id)
    if not post.post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_dict = post.post.model_dump()
    post_dict["id"] = str(post.post.id)
    ### code cũ
    # post_dict["comments"] = [comment for comment in post.post.comments if comment.statusComment != "hidden"]

    ### code mới
    # lọc comment trước
    filtered_comments = [
        comment for comment in post.post.comments 
        if comment.statusComment != "hidden"
    ]
    # convert từng comment sang dict + thêm thumbnails_url
    comments_with_url = []
    for comment in filtered_comments:
        comment_dict = comment.model_dump()
        
        if comment.thumbnails:
            comment_dict["thumbnails_url"] = [
                FileService.get_file_url(file_id) 
                for file_id in comment.thumbnails
            ]
        else:
            comment_dict["thumbnails_url"] = []
        
        comments_with_url.append(comment_dict)

    post_dict["comments"] = comments_with_url

    if post.post.thumbnails:
        post_dict["thumbnails_url"] = [FileService.get_file_url(file_id) for file_id in post.post.thumbnails]
    else:
        post_dict["thumbnails_url"] = []

    return {"post": post_dict}

@router.put("/update_post/{post_id}", response_model=UpdatePostResponse)
async def update_post(
    post_id: str,
    post: UpdatePostRequest,
    # current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    try:
        post.id = post_id
        updated = await service.update(post)
        if not updated:
            raise HTTPException(status_code=404, detail="Post not found")
        return updated
    except ModerationException as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Nội dung chỉnh sửa không được phép",
                "reason": e.reason,
                "violated_categories": e.violated_categories,
                "scores": e.scores,
                "confidence": e.confidence,
                "suggestion": "Vui lòng chỉnh sửa nội dung theo hướng dẫn và thử lại."
            }
        )

@router.delete("/delete_post/{post_id}", response_model=DeletePostResponse)
async def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    id = DeletePostRequest(id=post_id)
    success = await service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return success

@router.put("/update_comment/{post_id}", response_model=UpdatePostResponse)
async def update_comment(
    post_id: str,
    req: UpdateCommentStatusRequest,
    service: IPostService = Depends(get_post_service)
):
    updated = await service.update_comment_status(post_id, req.commentId, req.statusComment)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return updated



@router.put("/posts/{post_id}/react/{react_type}", response_model=UpdatePostReactResponse)
async def toggle_react(
    post_id: str,
    react_type: str,
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    user_email = current_user["sub"]
    valid_types = ["love", "like", "haha", "wow", "sad", "angry"]

    if react_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid react type")

    post = await service.find_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    react: React = post.react or React()
    current_list: List[str] = getattr(react, react_type)

    if user_email in current_list:
        current_list.remove(user_email)
    else:
        for r in valid_types:
            lst = getattr(react, r)
            if user_email in lst:
                lst.remove(user_email)
        current_list.append(user_email)

    await service.update_react(post_id, react)

    return UpdatePostReactResponse(message="Reaction updated", react=react)


@router.get("/get_post_by_email/{email}", response_model=GetPostByEmailResponse)
async def get_post_by_email(
    email: str,
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    req = GetPostByEmailRequest(email=email, ownerEmail=current_user["sub"])
    posts = await service.get_by_email(req)

    for p in posts.post_list:
        ## thumb comment
        if p.comments:
            for tb in p.comments:
                if tb.thumbnails: tb.thumbnails_url = [FileService.get_file_url(file_id) for file_id in tb.thumbnails]
        ## thumb comment
        if p.thumbnails:
            p.thumbnails_url = [FileService.get_file_url(file_id) for file_id in p.thumbnails]
        else:
            p.thumbnails_url = []
    return posts

@router.get("/get_my_post", response_model=GetAllPostResponse)
async def list_posts(
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    req = GetMyPostRequest(email=current_user["sub"])
    rs= await service.get_my_post(req)

    for p in rs.post_list:
        if p.comments:
            p.comments = [
                c for c in p.comments 
                if c.statusComment != "hidden"
            ]
            for tb in p.comments:
                if tb.thumbnails: tb.thumbnails_url = [FileService.get_file_url(file_id) for file_id in tb.thumbnails]
        if p.thumbnails:
            p.thumbnails_url = [FileService.get_file_url(file_id) for file_id in p.thumbnails]
        else:
            p.thumbnails_url = []
    return rs

@router.post("/share_post/{post_id}", response_model=AddPostResponse)
async def add_post(
    post_id: str,
    post: SharePostRequest,
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    post.postId = post_id
    post.postType = "share"
    post.createdBy = current_user["sub"]
    return await service.add(post)

@router.get("/get_post_of_day", response_model=GetPostOfDayResponse)
async def list_posts(
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    req = GetPostOfDayRequest()
    rs= await service.get_post_of_day(req)
    return rs

@router.get("/get_top_post", response_model=GetTopInteractedPostReponse)
async def list_posts(
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    req = GetTopInteractedPostRequest()
    rs= await service.get_top_interacted_posts_in_week(req)
    return rs

# @router.get("/get_top_post", response_model=GetTopInteractedPostReponse)
# async def list_posts(
#     current_user: dict = Depends(get_current_user),
#     service: IPostService = Depends(get_post_service)
# ):
#     if (current_user["role"] != "Administrator"):
#         raise HTTPException(status_code=403, detail="Failed!")
#     req = GetTopInteractedPostRequest()
#     rs= await service.get_top_interacted_posts_in_week(req)
#     return rs

@router.get("/get_post_suggest", response_model=GetPostSuggestResponse)
async def post_suggest(
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    if (current_user["role"] == "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    req = GetPostSuggestRequest(email=current_user["sub"])
    rs= await service.get_post_suggest(req)
    return rs

@router.get("/get_post_hidden_by_email", response_model=GetAllPostResponse)
async def get_post_hidden_by_email(
    current_user: dict = Depends(get_current_user),
    service: IPostService = Depends(get_post_service)
):
    req = GetMyPostRequest(email=current_user["sub"])
    posts = await service.get_post_hidden_by_email(req)
    return posts

