from dto.message.request.reset_unread_request import ResetUnreadRequest
from dto.message.response.conversation_response import ConversationResponse
from dto.message.response.reset_unread_response import ResetUnreadResponse
from repositories.conversation_repository import ConversationRepository
from services.interfaces.message_service_interface import IMessageService
from repositories.message_repository import MessageRepository
from models.message_model import Message
from repositories.account_repository import AccountRepository
from fastapi import HTTPException, status
from typing import List
from services.other.file_service import FileService
from websocket.connection_manager import manager


class MessageServiceImpl(IMessageService):
    async def send_message(
        self, sender_email: str, receiver_email: str, content: str, file: List[str], media: List[str]
    ) -> Message:
        # Kiểm tra tài khoản nhận có tồn tại
        receiver = await AccountRepository.find_by_email(receiver_email)
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receiver not found",
            )

        # Tạo conversation_id duy nhất
        conversation_id = "_".join(sorted([sender_email, receiver_email]))

        file_url: List[str] = []
        media_url: List[str] = []
        if len(file) > 0:
            for f in file:
                url = FileService.get_file_url(f)
                file_url.append(url)
        if len(media) > 0:
            for m in media:
                url = FileService.get_file_url(m)
                media_url.append(url)

        if len(file_url) > 0 and len(media_url) < 1:
            if content:
                msg = await MessageRepository.insert_message(
                    Message(
                        sender_email=sender_email,
                        receiver_email=receiver_email,
                        conversation_id=conversation_id,
                        content=content.strip(),
                        file=file,
                    )
                )
                msg.file = file_url
                msg.file_id = file
            else:
                msg = await MessageRepository.insert_message(
                    Message(
                        sender_email=sender_email,
                        receiver_email=receiver_email,
                        conversation_id=conversation_id,
                        file=file,
                    )
                )
                msg.file = file_url
                msg.file_id = file
        elif len(media_url) > 0 and len(file_url) < 1:
            if content:
                msg = await MessageRepository.insert_message(
                    Message(
                        sender_email=sender_email,
                        receiver_email=receiver_email,
                        conversation_id=conversation_id,
                        content=content.strip(),
                        media=media,
                    )
                )
                msg.media = media_url
            else:
                msg = await MessageRepository.insert_message(
                    Message(
                        sender_email=sender_email,
                        receiver_email=receiver_email,
                        conversation_id=conversation_id,
                        media=media,
                    )
                )
                msg.media = media_url
        elif len(media_url) > 0 and len(file_url) > 0:
            if content:
                msg = await MessageRepository.insert_message(
                    Message(
                        sender_email=sender_email,
                        receiver_email=receiver_email,
                        conversation_id=conversation_id,
                        content=content.strip(),
                        file=file,
                        media=media,
                    )
                )
                msg.file = file_url
                msg.file_id = file
                msg.media = media_url
            else:
                msg = await MessageRepository.insert_message(
                    Message(
                        sender_email=sender_email,
                        receiver_email=receiver_email,
                        conversation_id=conversation_id,
                        file=file,
                        media=media,
                    )
                )
                msg.file = file_url
                msg.file_id = file
                msg.media = media_url
        else:
            msg = await MessageRepository.insert_message(
            Message(
                sender_email=sender_email,
                receiver_email=receiver_email,
                conversation_id=conversation_id,
                content=content.strip(),
            )
        )

        # ⭐ Push real-time
        await manager.send_personal_message(msg)

         # ⭐ Gửi conversation_update cho receiver
        conv_resp = await ConversationRepository.get_conversation_response(
            user_email=receiver_email,
            other_email=sender_email
        )
        if conv_resp:
            payload = conv_resp.dict()
            payload["type"] = "conversation_update"
            await manager.send_json(payload, receiver_email)

        return msg

    async def get_conversation(
    self, user_a: str, user_b: str, skip: int = 0, limit: int = 50
    ) -> List[Message]:
        conversation_id = "_".join(sorted([user_a, user_b]))
        msgs = await MessageRepository.get_conversation(conversation_id, skip, limit)

        for msg in msgs:
            if msg.file:
                urls_file: List[List] = []
                for f in msg.file:
                    url = FileService.get_file_url(f)
                    urls_file.append(url)
                msg.file = urls_file
            if msg.media:
                urls_media: List[str] = []
                for m in msg.media:
                    url = FileService.get_file_url(m)
                    urls_media.append(url)
                msg.media = urls_media

        return sorted(msgs, key=lambda m: m.created_at)
    
    async def get_conversations(self, email: str) -> List[ConversationResponse]:
        rows = await MessageRepository.get_conversations_with_unread(email)
        return [ConversationResponse(**r) for r in rows]