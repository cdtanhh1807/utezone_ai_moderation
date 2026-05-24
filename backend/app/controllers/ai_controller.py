from fastapi import APIRouter, Depends, HTTPException
from core.dependency import get_ai_service, get_announce_service
from dto.ai.request.summarize_post_request import SummarizePostRequest
from dto.ai.response.summarize_post_response import SummarizePostResponse
from services.interfaces.ai_service_interface import IAIService
from utils.security import get_current_user


router = APIRouter()

@router.post("/summarize_post/{post_id}", response_model=SummarizePostResponse)
async def summarize_post(
    post_id: str,
    force_refresh: bool = False,
    service: IAIService = Depends(get_ai_service)
):
    request = SummarizePostRequest(post_id=post_id, force_refresh=force_refresh)
    response = await service.summarize_post(request)
    
    if not response.success:
        raise HTTPException(status_code=404 if "not found" in response.error_message else 400, 
                          detail=response.error_message)
    
    return response

@router.get("/get_existing_summary/{post_id}", response_model=SummarizePostResponse)
async def get_existing_summary(
    post_id: str,
    service: IAIService = Depends(get_ai_service)
):
    """
    Lấy summary đã có (không tạo mới)
    
    Nếu chưa có summary, trả về 404
    """
    response = await service.get_existing_summary(post_id)
    
    if not response:
        raise HTTPException(status_code=404, detail="Summary not found. Use POST to generate.")
    
    return response

@router.delete("/clear_summary_cache/{post_id}")
async def clear_summary_cache(post_id: str):
    """Xóa cache summary của bài viết"""
    from bson import ObjectId
    from core.database import db
    
    try:
        obj_id = ObjectId(post_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid post_id format")
    
    result = await db.post.update_one(
        {"_id": obj_id},
        {"$unset": {
            "ai_summary": "",
            "ai_summary_generated_at": "",
            "ai_summary_model": ""
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found or no cache to clear")
    
    return {"success": True, "message": "Summary cache cleared"}