from abc import ABC, abstractmethod
from dto.message.request.reset_unread_request import ResetUnreadRequest
from dto.message.response.conversation_response import ConversationResponse
from dto.message.response.reset_unread_response import ResetUnreadResponse
from models.message_model import Message
from typing import List


class IMessageService(ABC):
    @abstractmethod
    async def send_message(
        self, sender_email: str, receiver_email: str, content: str, file: List[str], media: List[str]
    ) -> Message:
        pass

    @abstractmethod
    async def get_conversation(
        self, user_a: str, user_b: str, skip: int = 0, limit: int = 50
    ) -> List[Message]:
        pass

    @abstractmethod
    async def get_conversations(self, email: str) -> List[ConversationResponse]:
        pass

    # @abstractmethod
    # async def reset_unread(self, user: str, req: ResetUnreadRequest) -> ResetUnreadResponse:
    #     pass
    