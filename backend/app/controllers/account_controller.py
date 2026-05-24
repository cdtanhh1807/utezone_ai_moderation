from email.quoprimime import unquote
from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Security, status
from dto.account.request.follow_block_request import FollowBlockRequest
from dto.account.request.get_all_account_request import GetAllAccountRequest
from dto.account.request.get_mod_request import GetModRequest
from dto.account.request.get_relation_request import GetRelationRequest
from dto.account.request.suggest_follow_request import SuggestFollowRequest
from dto.account.request.update_account_request import UpdateAccountRequest
from dto.account.request.update_account_t_request import UpdateAccountTRequest
from dto.account.response.account_info_response import AccountInfoResponse
from dto.account.response.follow_block_response import FollowBlockResponse
from dto.account.response.get_all_account_response import GetAllAccountResponse
from dto.account.response.get_mod_response import GetModResponse
from dto.account.response.get_relation_response import GetRelationResponse
from dto.account.response.suggest_follow_response import SuggestFollowResponse
from dto.account.response.update_account_response import UpdateAccountResponse
from dto.account.response.update_account_t_response import UpdateAccountTResponse
from repositories.account_repository import AccountRepository
from services.interfaces.account_service_interface import IAccountService
from core.dependency import get_account_service
from dto.account.request.login_request import LoginRequest
from dto.account.response.login_response import LoginResponse
from dto.account.request.register_user_request import RegisterUserRequest
from dto.account.response.register_user_response import RegisterUserResponse
from dto.auth.request.otp_request import OTPRequest
from dto.auth.response.otp_response import OTPResponse
from dto.account.request.logout_request import LogoutRequest
from dto.account.response.logout_response import LogoutResponse
from dto.account.request.forgot_password_request import ForgotPasswordRequest
from dto.account.response.forgot_password_response import ForgotPasswordResponse
from services.other.file_service import FileService
from utils.security import create_access_token, get_current_user

from dto.account.request.google_auth_request import GoogleAuthRequest
import requests

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter() 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/account/login")

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: IAccountService = Depends(get_account_service)
):
    data = LoginRequest(username=form_data.username, password=form_data.password)
    account = await service.authenticate_user(data)
    if not account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": account.email, "role": account.role, "per": account.permission.pernum})
    return LoginResponse(access_token=token) 

@router.post("/register", response_model=OTPResponse)
async def register(
    data: RegisterUserRequest,
    service: IAccountService = Depends(get_account_service)
):
    await service.register_user(data)
    return OTPResponse(message="OTP has been sent to your email. Please verify within 3 minutes.")

@router.post("/verify-otp", response_model=RegisterUserResponse)
async def verify_otp(
    data: OTPRequest,
    service: IAccountService = Depends(get_account_service)
):
    account = await service.verify_otp(data)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP verification failed"
        )
    return account

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    token_in: str = Security(oauth2_scheme),
    service: IAccountService = Depends(get_account_service)
):
    logout_req = LogoutRequest(token=token_in)
    res = await service.logout_user(logout_req)
    if not res.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )
    return res

@router.post("/forgot-password", response_model=OTPResponse)
async def forgot_password(
    email: ForgotPasswordRequest,
    service: IAccountService = Depends(get_account_service)
):
    await service.forgot_password(email)
    return OTPResponse(message="OTP has been sent to your email. Please verify within 3 minutes.")

@router.post("/change-password", response_model=ForgotPasswordResponse)
async def change_password(
    data: ForgotPasswordRequest,
    service: IAccountService = Depends(get_account_service)
):
    rs = await service.change_password(data)
    if rs.success == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="failed"
        )
    
    return rs

@router.post("/google-login")
async def google_login(
    google_req: GoogleAuthRequest,
    service: IAccountService = Depends(get_account_service)
):
    account = await service.login_with_google(google_req)
    if not account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": account.email, "role": account.role, "per": account.permission.pernum})
    return LoginResponse(access_token=token) 

@router.get("/get_all_account", response_model=GetAllAccountResponse)
async def list_accounts(
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):  
    if (current_user["role"] != "Administrator"):
        raise HTTPException(status_code=403, detail="Failed!")
    account_list = GetAllAccountRequest()
    return await service.get_all(account_list)

@router.put("/update_account/{account_id}", response_model=UpdateAccountResponse)
async def update_account(
    account_id: str,
    account: UpdateAccountRequest,
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    account.id = account_id
    updated = await service.update(account)
    if not updated:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated

@router.put("/follow", response_model=FollowBlockResponse)
async def follow(
    account: FollowBlockRequest,
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    rs = await service.follow(account)
    if rs.message == False:
        raise HTTPException(status_code=404, detail="Account not found")
    return rs

@router.put("/un_follow", response_model=FollowBlockResponse)
async def un_follow(
    account: FollowBlockRequest,
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    rs = await service.un_follow(account)
    if rs.message == False:
        raise HTTPException(status_code=404, detail="Account not found")
    return rs

@router.put("/block", response_model=FollowBlockResponse)
async def block(
    account: FollowBlockRequest,
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    rs = await service.block(account)
    if rs.message == False:
        raise HTTPException(status_code=404, detail="Account not found")
    return rs

@router.put("/un_block", response_model=FollowBlockResponse)
async def un_block(
    account: FollowBlockRequest,
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    rs = await service.un_block(account)
    if rs.message == False:
        raise HTTPException(status_code=404, detail="Account not found")
    return rs


@router.put("/update_account", response_model=UpdateAccountTResponse)
async def update_account(
    data: UpdateAccountTRequest = Body(...),
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    email = current_user["sub"]
    update_data = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    success = await service.update_user_info(email=email, user_info=update_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update account info")
    return UpdateAccountTResponse(message="Account info updated successfully", success=True)

@router.get("/account_info", response_model=AccountInfoResponse)
async def get_account_info(
    email: Optional[str],
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    target_email = email    
    account = await service.get_account_by_email(target_email)    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    user_info = account.userInfo.dict() if account.userInfo else {}

    avatar_file_id = user_info.get("avatar")
    if avatar_file_id:
        avatar_url = FileService.get_file_url(avatar_file_id, expires_seconds=3600)
        user_info["avatar"] = avatar_url
    
    return AccountInfoResponse(**user_info)

@router.get("/account_relation/{email}", response_model=GetRelationResponse)
async def get_account_relation(
    email: str,
    # current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    req = GetRelationRequest(email=email)
    relation = await service.get_relation(req)    
    if not relation:
        raise HTTPException(status_code=404, detail="Not found")
    return relation


@router.get("/get_mod", response_model=GetModResponse)
async def get_mod(
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):  
    req = GetModRequest()
    return await service.get_mod(req)

@router.get("/suggest_follow", response_model=SuggestFollowResponse)
async def suggest_follow(
    # limit: int = Query(default=20, ge=1, le=50),
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    service: IAccountService = Depends(get_account_service)
):
    req = SuggestFollowRequest(email=current_user["sub"], limit=limit)
    return await service.get_suggest_follow(req)