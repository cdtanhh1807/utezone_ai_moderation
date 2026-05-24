from dto.story.request.delete_story_requesy import DeleteStoryRequest
from dto.story.response.add_story_response import AddStoryResponse
from dto.story.response.delete_story_response import DeleteStoryResponse
from dto.story.response.today_story_response import UserStoryGroup
from repositories.account_repository import AccountRepository
from repositories.story_repository import StoryRepository
from services.interfaces.story_service_interface import IStoryService
from services.other.file_service import FileService
from dto.story.response.today_story_response import UserStoryGroup, Story
from typing import List, Optional
from models.story_model import React

class StoryServiceImpl(IStoryService):

    async def add(self, story_data: dict) -> AddStoryResponse:
        if story_data.get("react") is None:
            story_data["react"] = React().dict()

        new_story = await StoryRepository.add_story(story_data)
        if new_story:
            return AddStoryResponse(
                success=True,
                message="Story added successfully",
                story=new_story
            )
        return AddStoryResponse(
            success=False,
            message="Failed to add story"
        )

    async def find_by_user(self, user_id: str):
        return await StoryRepository.find_by_user(user_id)

    async def find_all_active(self):
        return await StoryRepository.find_all_active()

    async def get_today_stories(self, email: str) -> List[UserStoryGroup]:
        dic_acc = await AccountRepository.find_by_email(email)
        stories = await StoryRepository.find_today_stories(dic_acc)
        grouped = {}

        for story in stories:
            uid = story["createdBy"]

            if story.get("thumbnails") and len(story["thumbnails"]) > 0:
                story["mediaUrls"] = [
                    FileService.get_file_url(file_id) for file_id in story["thumbnails"]
                ]
            else:
                story["mediaUrls"] = []

            # Gán url cho music nếu có fileid
            if story.get("music") and story["music"].get("fileid"):
                story["music"]["url"] = FileService.get_file_url(story["music"]["fileid"])

            if uid not in grouped:
                grouped[uid] = []

            grouped[uid].append(story)

        result: List[UserStoryGroup] = []

        for uid, story_list in grouped.items():
            sorted_story = sorted(story_list, key=lambda s: s["createdAt"])
            result.append(UserStoryGroup(
                userId=uid,
                stories=[Story(**s) for s in sorted_story],
                latestStoryAt=str(sorted_story[-1]["createdAt"])
            ))

        # Sắp xếp user theo latestStoryAt giảm dần
        result.sort(key=lambda x: x.latestStoryAt, reverse=True)
        return result
    
    async def delete(self, story_id: DeleteStoryRequest) -> Optional[DeleteStoryResponse]:
        rs = await StoryRepository.delete(story_id.id)
        if rs:
            return DeleteStoryResponse(success=True, message="Deleted")
        else:
            return None
