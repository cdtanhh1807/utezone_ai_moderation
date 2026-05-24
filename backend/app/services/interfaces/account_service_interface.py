from abc import ABC, abstractmethod
from typing import Optional
from dto.account.request.follow_block_request import FollowBlockRequest
from dto.account.request.get_all_account_request import GetAllAccountRequest
from dto.account.request.get_mod_request import GetModRequest
from dto.account.request.get_relation_request import GetRelationRequest
from dto.account.request.google_auth_request import GoogleAuthRequest
from dto.account.request.register_user_request import RegisterUserRequest
from dto.account.request.suggest_follow_request import SuggestFollowRequest
from dto.account.request.update_account_request import UpdateAccountRequest
from dto.account.response.follow_block_response import FollowBlockResponse
from dto.account.response.get_all_account_response import GetAllAccountResponse
from dto.account.response.get_mod_response import GetModResponse
from dto.account.response.get_relation_response import GetRelationResponse
from dto.account.response.register_user_response import RegisterUserResponse
from dto.account.response.suggest_follow_response import SuggestFollowResponse
from dto.account.response.update_account_response import UpdateAccountResponse
from dto.auth.request.otp_request import OTPRequest
from dto.auth.response.otp_response import OTPResponse
from models.account_model import Account
from dto.account.request.login_request import LoginRequest
from dto.account.request.logout_request import LogoutRequest
from dto.account.response.logout_response import LogoutResponse
from dto.account.request.forgot_password_request import ForgotPasswordRequest
from dto.account.response.forgot_password_response import ForgotPasswordResponse

class IAccountService(ABC):

    @abstractmethod
    async def register_user(self, register_user_req: RegisterUserRequest) -> Optional[OTPResponse]:
        pass    

    @abstractmethod
    async def authenticate_user(self, login_req: LoginRequest) -> Optional[Account]:
        pass

    @abstractmethod
    async def verify_otp(self, otp_req: OTPRequest) -> Optional[RegisterUserResponse]:
        pass

    @abstractmethod
    async def logout_user(self, logout_req: LogoutRequest) -> Optional[LogoutResponse]:
        pass

    @abstractmethod
    async def forgot_password(self, forgot_password_req: ForgotPasswordRequest) -> None:
        pass

    @abstractmethod
    async def change_password(self, change_password_req: ForgotPasswordRequest) -> Optional[ForgotPasswordResponse]:
        pass

    @abstractmethod
    async def login_with_google(self, google_req: GoogleAuthRequest) -> Optional[Account]:
        pass

    @abstractmethod
    async def get_all(self, post_list: GetAllAccountRequest) -> GetAllAccountResponse:
        pass

    @abstractmethod
    async def update(self, account_req: UpdateAccountRequest) -> Optional[UpdateAccountResponse]:
        pass

    @abstractmethod
    async def follow(self, req: FollowBlockRequest) -> Optional[FollowBlockResponse]:
        pass

    @abstractmethod
    async def un_follow(self, req: FollowBlockRequest) -> Optional[FollowBlockResponse]:
        pass

    @abstractmethod
    async def block(self, req: FollowBlockRequest) -> Optional[FollowBlockResponse]:
        pass

    @abstractmethod
    async def un_block(self, req: FollowBlockRequest) -> Optional[FollowBlockResponse]:
        pass


    @abstractmethod
    async def update_user_info(self, email: str, user_info: UpdateAccountRequest) -> bool:
        pass

    @abstractmethod
    async def get_account_by_email(self, email: str) -> Optional[Account]:
        pass

    @abstractmethod
    async def get_relation(self, req: GetRelationRequest) -> Optional[GetRelationResponse]:
        pass

    @abstractmethod
    async def get_mod(self, account_list: GetModRequest) -> Optional[GetModResponse]:
        pass

    @abstractmethod
    async def get_suggest_follow(self, req: SuggestFollowRequest) -> SuggestFollowResponse:
        pass