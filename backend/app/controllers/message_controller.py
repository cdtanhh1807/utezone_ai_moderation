from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from typing import List
from dto.message.request.mark_read_request import MarkReadRequest
from dto.message.request.reset_unread_request import ResetUnreadRequest
from dto.message.request.send_message_request import SendMessageRequest
from dto.message.response.conversation_response import ConversationResponse
from dto.message.response.reset_unread_response import ResetUnreadResponse
from repositories.conversation_repository import ConversationRepository
from services.interfaces.message_service_interface import IMessageService
from utils.security import create_access_token, get_current_user
from core.dependency import get_message_service
from models.message_model import Message
from core.database import db

router = APIRouter() 

@router.post("/send", response_model=Message)
async def send_message(
    req: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    service: IMessageService = Depends(get_message_service),
):
    file_req: List[str] = []
    media_req: List[str] = []
    content: str = None
    if req.media:
        media_req = req.media
    if req.file:
        file_req = req.file
    if req.content:
        content = req.content

    return await service.send_message(
        sender_email=current_user["sub"],
        receiver_email=req.receiver_email,
        content=content,
        file=file_req,
        media=media_req,
    )


@router.get("/conversation/{other_email}", response_model=List[Message])
async def get_conversation(
    other_email: str,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    service: IMessageService = Depends(get_message_service),
):
    return await service.get_conversation(
        user_a=current_user["sub"],
        user_b=other_email,
        skip=skip,
        limit=limit,
    )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    service: IMessageService = Depends(get_message_service),
):
    return await service.get_conversations(current_user["sub"])

@router.post("/mark-read")
async def mark_read(
    req: MarkReadRequest,
    current_user: dict = Depends(get_current_user),
):
    await ConversationRepository.update_last_seen(
        user=current_user["sub"],
        other=req.other_email,
        when=datetime.now(timezone.utc)
    )
    return {"ok": True}