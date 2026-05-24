from fastapi import APIRouter, Depends, HTTPException
from dto.story.request.add_story_request import AddStoryRequest
from dto.story.request.delete_story_requesy import DeleteStoryRequest
from dto.story.response.add_story_response import AddStoryResponse
from dto.story.response.delete_story_response import DeleteStoryResponse
from dto.story.response.today_story_response import GetTodayStoryResponse
from services.interfaces.story_service_interface import IStoryService
from services.other.file_service import FileService
from core.dependency import get_story_service
from utils.security import get_current_user
from datetime import datetime, timezone

router = APIRouter()

@router.post("/add_story", response_model=AddStoryResponse)
async def add_story(
    story: AddStoryRequest,
    current_user: dict = Depends(get_current_user),
    service: IStoryService = Depends(get_story_service)
):
    user_id = current_user.get("sub")
    story_data = story.dict()
    story_data["createdBy"] = user_id
    story_data["createdAt"] = datetime.now(timezone.utc)
    story_data["status"] = story_data.get("status", "active")
    return await service.add(story_data)


@router.get("/user/{user_id}")
async def get_user_stories(
    user_id: str,
    service: IStoryService = Depends(get_story_service)
):
    return await service.find_by_user(user_id)


@router.get("/active")
async def get_all_active_stories(
    service: IStoryService = Depends(get_story_service)
):
    storys = await service.find_all_active()

    for p in storys.story_list:
        if p.mediaUrls:
            p.mediaUrls = [
                FileService.get_file_url(file_id) 
                for file_id in p.mediaUrls
            ]
        else:
            p.mediaUrls = []
    return storys


@router.get("/get_today_story", response_model=GetTodayStoryResponse)
async def get_today_story(
    current_user: dict = Depends(get_current_user),
    service: IStoryService = Depends(get_story_service)
):
    data = await service.get_today_stories(current_user["sub"])
    return GetTodayStoryResponse(
        success=True,
        data=data,
        message="Get today's stories successfully"
    )

@router.delete("/delete_story/{story_id}", response_model=DeleteStoryResponse)
async def delete_post(
    story_id: str,
    current_user: dict = Depends(get_current_user),
    service: IStoryService = Depends(get_story_service)
):
    id = DeleteStoryRequest(id=story_id)
    success = await service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return success
