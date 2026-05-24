from datetime import datetime
from io import BytesIO
import os

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Request
from typing import Optional
from meeting.services.channel_service import channel_service
from meeting.models.channel_model import (
    CreateChannelRequest, UpdateChannelRequest,
    CreateChatRoomRequest, UpdateChatRoomRequest,
    JoinChannelRequest, ApproveMemberRequest,
    SendMessageRequest
)
from utils.security import get_current_user
import httpx

from fastapi import BackgroundTasks
from meeting.services.moderation_service import moderate_text_message

router = APIRouter(prefix="/channels", tags=["channels"])

#=================
from meeting.websocket.manager import ws_manager

@router.websocket("/ws/{channel_id}")
async def channel_websocket(websocket: WebSocket, channel_id: str):
    token = websocket.query_params.get("token")
    print(f"[WS] New connection attempt, channel_id={channel_id}, token={token[:20]}...")
    if not token:
        print("[WS] No token")
        await websocket.close(code=1008)
        return
    try:
        current_user = await get_current_user(token)
        email = current_user["sub"]
        print(f"[WS] Authenticated user: {email}")
    except Exception as e:
        print(f"[WS] Auth error: {e}")
        await websocket.close(code=1008)
        return

    channel = await channel_service.get_channel(channel_id)
    if not channel:
        print(f"[WS] Channel {channel_id} not found")
        await websocket.close(code=1008, reason="Channel không tồn tại")
        return
    is_member = any(m.email == email and m.status == "approved" for m in channel.members)
    if not is_member:
        print(f"[WS] User {email} not member of channel {channel_id}")
        await websocket.close(code=1008, reason="Bạn không phải thành viên")
        return

    await ws_manager.connect(websocket, channel_id)
    #await ws_manager.broadcast(channel_id, {"type": "test", "message": "Hello from server"})
    print(f"[WS] User {email} connected to channel {channel_id}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel_id)
        print(f"[WS] User {email} disconnected")

#=================
def _extract_token(request: Request) -> str:
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return ""


async def get_fullname_from_api(email: str, token: str = "") -> str:
    if not token or not token.strip():
        return email.split('@')[0]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/account/account_info?email={email}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("fullName") or email.split('@')[0]
    except Exception as e:
        print(f"Error fetching fullName from API: {e}")
    return email.split('@')[0]


# ==================== CHANNEL CRUD ====================

@router.post("/create")
async def create_channel(
    req: CreateChannelRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    email = current_user["sub"]
    token = _extract_token(request)
    full_name = await get_fullname_from_api(email, token)
    try:
        channel = await channel_service.create_channel(
            owner_email=email, owner_name=full_name,
            name=req.name, description=req.description,
            require_approval=req.require_approval
        )
        return channel.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-channels")
async def get_my_channels(current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    channels = await channel_service.get_my_channels(email)
    return {"channels": channels}


@router.get("/{channel_id}")
async def get_channel(channel_id: str, current_user: dict = Depends(get_current_user)):
    channel = await channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel không tồn tại")
    email = current_user["sub"]
    is_member = any(m.email == email and m.status == "approved" for m in channel.members)
    is_owner = channel.owner_email == email
    result = channel.model_dump()
    result["is_member"] = is_member
    result["is_owner"] = is_owner
    if not is_member and not is_owner:
        result["members"] = [{"role": m.role, "status": m.status} for m in channel.members if m.status == "approved"]
        result["member_count"] = len([m for m in channel.members if m.status == "approved"])
    return result


@router.put("/{channel_id}")
async def update_channel(channel_id: str, req: UpdateChannelRequest, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    try:
        channel = await channel_service.update_channel(
            channel_id=channel_id, owner_email=email,
            name=req.name, description=req.description,
            avatar=req.avatar, require_approval=req.require_approval
        )
        return channel.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{channel_id}/invite-code")
async def get_invite_code(channel_id: str, current_user: dict = Depends(get_current_user)):
    channel = await channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel không tồn tại")
    email = current_user["sub"]
    if channel.owner_email != email:
        raise HTTPException(status_code=403, detail="Chỉ chủ channel mới có thể xem invite code")
    return {"invite_code": channel.invite_code, "invite_url": f"/channels/join?code={channel.invite_code}"}


# ==================== CHANNEL MEMBERSHIP ====================

@router.post("/join")
async def join_channel(req: JoinChannelRequest, request: Request, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    token = _extract_token(request)
    full_name = await get_fullname_from_api(email, token)
    result = await channel_service.join_channel(email=email, username=full_name, invite_code=req.invite_code, channel_id=None)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Không thể tham gia channel"))
    return result


@router.post("/join/{channel_id}")
async def join_channel_by_id(channel_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    token = _extract_token(request)
    full_name = await get_fullname_from_api(email, token)
    result = await channel_service.join_channel(email=email, username=full_name, channel_id=channel_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Không thể tham gia channel"))
    return result


@router.post("/{channel_id}/leave")
async def leave_channel(channel_id: str, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    result = await channel_service.leave_channel(email, channel_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.get("/{channel_id}/members")
async def get_channel_members(channel_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    channel = await channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel không tồn tại")
    is_member = any(m.email == email and m.status == "approved" for m in channel.members)
    is_owner = channel.owner_email == email
    if not is_member and not is_owner:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên")
    
    members = []
    for m in channel.members:
        # Gọi API account_info để lấy avatar
        avatar_url = None
        try:
            async with httpx.AsyncClient() as client:
                token = _extract_token(request)
                resp = await client.get(
                    f"http://localhost:8000/account/account_info?email={m.email}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    avatar_url = data.get("avatar")
        except Exception as e:
            print(f"Error fetching avatar for {m.email}: {e}")
        
        members.append({
            "email": m.email,
            "username": m.username or m.email.split('@')[0],
            "role": m.role,
            "status": m.status,
            "is_online": False,  # sẽ được gán sau
            "avatar": avatar_url
        })
    return {"members": members}


@router.get("/{channel_id}/pending-members")
async def get_pending_members(channel_id: str, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    pending = await channel_service.get_pending_members(channel_id, email)
    return {"pending_members": pending}

@router.post("/{channel_id}/approve")
async def approve_member(channel_id: str, req: ApproveMemberRequest, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    result = await channel_service.approve_member(channel_id, email, req.email, req.approve)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    # Nếu approve thành công, broadcast để member được thêm vào channel
    if req.approve:
        # Lấy thông tin member vừa được approve
        channel = await channel_service.get_channel(channel_id)
        member_info = None
        for m in channel.members:
            if m.email == req.email and m.status == "approved":
                member_info = {
                    "email": m.email,
                    "username": m.username,
                    "role": m.role,
                    "status": m.status,
                    "avatar": None  # có thể lấy thêm
                }
                break
        if member_info:
            await ws_manager.broadcast(channel_id, {
                "type": "member_approved",
                "member": member_info
            })
    return result


@router.post("/{channel_id}/kick/{member_email}")
async def kick_member(channel_id: str, member_email: str, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]

    result = await channel_service.kick_member(channel_id, email, member_email)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    await ws_manager.broadcast(channel_id, {
        "type": "member_kicked",
        "channel_id": channel_id,
        "member_email": member_email,
        "kicked_by": email
    })

    return result


# ==================== CHAT ROOM CRUD ====================
@router.post("/{channel_id}/chatrooms")
async def create_chat_room(channel_id: str, req: CreateChatRoomRequest, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    try:
        chatroom = await channel_service.create_chat_room(
            channel_id=channel_id, owner_email=email,
            name=req.name, description=req.description, room_type=req.room_type
        )
        # Broadcast room mới
        await ws_manager.broadcast(channel_id, {
            "type": "chatroom_created",
            "chatroom": chatroom.model_dump()
        })
        return chatroom.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{channel_id}/chatrooms")
async def get_channel_chat_rooms(channel_id: str, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    channel = await channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel không tồn tại")
    is_member = any(m.email == email and m.status == "approved" for m in channel.members)
    if not is_member:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của channel này")
    chatrooms = await channel_service.get_channel_chat_rooms(channel_id)
    return {"chatrooms": chatrooms}


@router.put("/chatrooms/{room_id}")
async def update_chat_room(room_id: str, req: UpdateChatRoomRequest, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    try:
        chatroom = await channel_service.update_chat_room(room_id=room_id, owner_email=email, name=req.name, description=req.description)
        return chatroom.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/chatrooms/{room_id}")
async def delete_chat_room(room_id: str, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    # Lấy channel_id trước khi xóa
    chatroom = await channel_service.get_chat_room(room_id)
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chat room không tồn tại")
    channel_id = chatroom.channel_id
    success = await channel_service.delete_chat_room(room_id, email)
    if not success:
        raise HTTPException(status_code=403, detail="Không có quyền hoặc chat room không tồn tại")
    await ws_manager.broadcast(channel_id, {"type": "chatroom_deleted", "room_id": room_id})
    return {"status": "deleted"}


@router.post("/chatrooms/{room_id}/start-meeting")
async def start_meeting_in_chatroom(room_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    token = _extract_token(request)
    full_name = await get_fullname_from_api(email, token)
    try:
        result = await channel_service.start_meeting_in_chatroom(room_id=room_id, owner_email=email, host_name=full_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== MESSAGES ====================

@router.post("/chatrooms/{room_id}/messages")
async def send_message(room_id: str, req: SendMessageRequest, request: Request, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    token = _extract_token(request)
    full_name = await get_fullname_from_api(email, token)
    chatroom = await channel_service.get_chat_room(room_id)
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chat room không tồn tại")
    try:
        message = await channel_service.send_message(
            room_id=room_id, channel_id=chatroom.channel_id,
            sender_email=email, sender_name=full_name,
            content=req.content,
            msg_type=req.msg_type,
            file_name=req.file_name
        )
        message_dict = message.model_dump()
        # Broadcast tin nhắn mới cho tất cả client trong channel
        print(f"[BROADCAST] Sending to channel {chatroom.channel_id}, message_id={message.message_id}")
        if isinstance(message_dict.get('created_at'), datetime):
            message_dict['created_at'] = message_dict['created_at'].isoformat()
        
        await ws_manager.broadcast(chatroom.channel_id, {
            "type": "new_message",
            "message": message_dict
        })

        #AI
        if req.msg_type == "text":
            rules = await channel_service.get_channel_rules(chatroom.channel_id)
            if rules and rules.enabled and "text" in rules.enabled_types:
                background_tasks.add_task(
                    moderate_text_message,
                    channel_id=chatroom.channel_id,
                    message_id=message.message_id,
                    content=req.content,
                    sender_email=email,
                    room_id=room_id
                )

        return message_dict
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/chatrooms/{room_id}/messages")
async def get_messages(room_id: str, limit: int = 50, before: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    chatroom = await channel_service.get_chat_room(room_id)
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chat room khong ton tai")
    messages = await channel_service.get_messages(room_id, limit, before)
    return {"messages": messages}


@router.delete("/messages/{message_id}")
async def delete_message_by_owner(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    email = current_user["sub"]

    result = await channel_service.delete_message_by_owner(
        message_id=message_id,
        owner_email=email
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    await ws_manager.broadcast(result["channel_id"], {
        "type": "message_removed",
        "message_id": result["message_id"],
        "room_id": result["room_id"],
        "user_email": email,
        "reason": "Tin nhắn đã bị chủ channel xóa"
    })

    return {
        "success": True,
        "message": "Đã xóa tin nhắn",
        "message_id": result["message_id"]
    }

# ==================== USER SESSION ====================

@router.post("/session/set")
async def set_user_session(channel_id: Optional[str] = None, chat_room_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    try:
        result = await channel_service.set_user_session(email, channel_id, chat_room_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/my")
async def get_my_session(current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    session = await channel_service.get_user_session(email)
    return session or {"email": email, "current_channel_id": None, "current_chat_room_id": None}


@router.post("/session/clear")
async def clear_my_session(current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    await channel_service.clear_user_session(email)
    return {"status": "cleared"}


@router.get("/{channel_id}/online-users")
async def get_online_users_in_channel(channel_id: str, current_user: dict = Depends(get_current_user)):
    sessions = await channel_service.get_online_users_in_channel(channel_id)
    return {"online_users": sessions}


@router.get("/chatrooms/{room_id}/online-users")
async def get_online_users_in_chatroom(room_id: str, current_user: dict = Depends(get_current_user)):
    sessions = await channel_service.get_online_users_in_chatroom(room_id)
    return {"online_users": sessions}

@router.get("/files/{file_id}")
async def get_file(file_id: str, current_user: dict = Depends(get_current_user)):
    """Lấy URL tạm thời của file (yêu cầu đăng nhập)"""
    try:
        from services.other.file_service import FileService
        url = FileService.get_file_url(file_id)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")

# ==================== FILE UPLOAD ====================

@router.post("/chatrooms/{room_id}/upload")
async def upload_chat_file(
    room_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload file cho chat trong channel room.

    Nếu channel bật kiểm duyệt cho loại file tương ứng thì kiểm duyệt trước khi upload.
    Quan trọng: moderation fail/429/parse lỗi sẽ bị chặn, không cho upload lọt qua.
    """
    email = current_user["sub"]

    chatroom = await channel_service.get_chat_room(room_id)
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chat room không tồn tại")

    channel = await channel_service.get_channel(chatroom.channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel không tồn tại")

    is_member = any(m.email == email and m.status == "approved" for m in channel.members)
    if not is_member:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của channel này")

    try:
        from services.other.file_service import FileService
        from meeting.services.moderation_service import moderate_file
        import tempfile

        content_type = file.content_type or ""
        filename = file.filename or "uploaded_file"

        if content_type.startswith("image/"):
            media_type = "image"
        elif content_type.startswith("video/"):
            media_type = "video"
        else:
            media_type = "document"

        rules = await channel_service.get_channel_rules(chatroom.channel_id)
        should_moderate = False

        if rules and rules.enabled:
            if media_type == "image" and "image" in rules.enabled_types:
                should_moderate = True
            elif media_type == "video" and "video" in rules.enabled_types:
                should_moderate = True
            elif media_type == "document" and "file" in rules.enabled_types:
                should_moderate = True

        if should_moderate:
            content = await file.read()
            suffix = os.path.splitext(filename)[1] or ""
            tmp_path = None

            try:
                fd, tmp_path = tempfile.mkstemp(suffix=suffix)
                with os.fdopen(fd, "wb") as tmp:
                    tmp.write(content)

                moderation = await moderate_file(
                    channel_id=chatroom.channel_id,
                    file_path=tmp_path,
                    filename=filename,
                    media_type=media_type,
                    sender_email=email,
                    room_id=room_id
                )

                print(f"[FILE_MODERATION] {filename}: {moderation}")

                if not moderation.get("approved", False):
                    reason = moderation.get(
                        "reason",
                        "Nội dung vi phạm hoặc hệ thống kiểm duyệt đang quá tải"
                    )
                    reason_lower = str(reason).lower()

                    service_error_keywords = [
                        "rate limited",
                        "unavailable",
                        "empty response",
                        "invalid response",
                        "unexpected response",
                        "missing approved",
                        "not boolean",
                        "cannot extract",
                        "file moderation error",
                        "service unavailable",
                        "không thể đọc kết quả",
                        "không khả dụng",
                        "quá tải",
                    ]

                    if any(keyword in reason_lower for keyword in service_error_keywords):
                        raise HTTPException(status_code=503, detail={
                            "error": "AI kiểm duyệt không khả dụng",
                            "reason": "Không thể kiểm duyệt file lúc này, vui lòng thử lại sau"
                        })

                    raise HTTPException(status_code=400, detail={
                        "error": "File không được phép upload",
                        "reason": reason
                    })

            finally:
                if tmp_path:
                    try:
                        os.unlink(tmp_path)
                    except Exception as cleanup_err:
                        print(f"[UPLOAD_CLEANUP] Không thể xóa file tạm {tmp_path}: {cleanup_err}")

            # Reset stream để FileService có thể đọc lại file sau khi moderation đã đọc hết.
            file.file = BytesIO(content)
            file.size = len(content)

        file_id = await FileService.upload_file(file)
        url = FileService.get_file_url(file_id)

        return {
            "file_id": file_id,
            "url": url,
            "filename": filename,
            "content_type": content_type
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[UPLOAD_ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{channel_id}")
async def delete_channel(channel_id: str, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    success = await channel_service.delete_channel(channel_id, email)
    if not success:
        raise HTTPException(status_code=403, detail="Không có quyền hoặc channel không tồn tại")
    # Broadcast cho tất cả member (thông qua WebSocket manager)
    await ws_manager.broadcast(channel_id, {"type": "channel_deleted", "channel_id": channel_id})
    return {"status": "deleted"}

@router.post("/chatrooms/{room_id}/mark-read")
async def mark_room_read(room_id: str, current_user: dict = Depends(get_current_user)):
    """Đánh dấu user đã đọc tin nhắn trong room"""
    email = current_user["sub"]
    # Lấy tin nhắn mới nhất để lưu last_read_message_id (tuỳ chọn)
    last_msg = await channel_service.get_last_message(room_id)  # cần implement
    msg_id = last_msg.message_id if last_msg else None
    await channel_service.update_read_status(email, room_id, msg_id)
    return {"status": "ok"}

@router.get("/{channel_id}/unread-counts")
async def get_unread_counts(channel_id: str, current_user: dict = Depends(get_current_user)):
    """Lấy số tin nhắn chưa đọc cho từng room trong channel"""
    email = current_user["sub"]
    counts = await channel_service.get_unread_counts_for_channel(email, channel_id)
    return {"unread_counts": counts}

# @router.post("/{channel_id}/avatar")
# async def upload_channel_avatar(
#     channel_id: str,
#     request: Request,
#     file: UploadFile = File(...),
#     current_user: dict = Depends(get_current_user)
# ):
#     email = current_user["sub"]
#     channel = await channel_service.get_channel(channel_id)
#     if not channel:
#         raise HTTPException(status_code=404, detail="Channel không tồn tại")
#     if channel.owner_email != email:
#         raise HTTPException(status_code=403, detail="Chỉ chủ channel mới có thể thay đổi avatar")
    
#     try:
#         from services.other.file_service import FileService
#         file_id = await FileService.upload_file(file)
#         avatar_url = FileService.get_file_url(file_id)
#         # Cập nhật avatar trong database
#         await channel_service.update_channel(channel_id, email, avatar=avatar_url)
#         # Broadcast cập nhật avatar đến tất cả member
#         await ws_manager.broadcast(channel_id, {
#             "type": "channel_avatar_updated",
#             "avatar_url": avatar_url
#         })
#         return {"avatar_url": avatar_url}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@router.post("/{channel_id}/avatar")
async def upload_channel_avatar(
    channel_id: str,
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    email = current_user["sub"]
    channel = await channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel không tồn tại")
    if channel.owner_email != email:
        raise HTTPException(status_code=403, detail="Chỉ chủ channel mới có thể thay đổi avatar")
    
    try:
        from services.other.file_service import FileService
        file_id = await FileService.upload_file(file)
        # Lưu file_id thay vì URL
        await channel_service.update_channel(channel_id, email, avatar=file_id)
        # Broadcast file_id (không phải URL)
        await ws_manager.broadcast(channel_id, {
            "type": "channel_avatar_updated",
            "file_id": file_id
        })
        return {"file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.delete("/{channel_id}/avatar")
# async def delete_channel_avatar(
#     channel_id: str,
#     current_user: dict = Depends(get_current_user)
# ):
#     email = current_user["sub"]
#     channel = await channel_service.get_channel(channel_id)
#     if not channel or channel.owner_email != email:
#         raise HTTPException(status_code=403, detail="Không có quyền")
#     await channel_service.update_channel(channel_id, email, avatar=None)
#     await ws_manager.broadcast(channel_id, {
#         "type": "channel_avatar_updated",
#         "avatar_url": None
#     })
#     return {"status": "deleted"}
@router.delete("/{channel_id}/avatar")
async def delete_channel_avatar(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    email = current_user["sub"]
    channel = await channel_service.get_channel(channel_id)
    if not channel or channel.owner_email != email:
        raise HTTPException(status_code=403, detail="Không có quyền")
    await channel_service.update_channel(channel_id, email, avatar=None)
    await ws_manager.broadcast(channel_id, {
        "type": "channel_avatar_updated",
        "file_id": None
    })
    return {"status": "deleted"}

@router.get("/chatrooms/{room_id}/media")
async def get_room_media(room_id: str, current_user: dict = Depends(get_current_user)):
    """Lấy danh sách ảnh và video trong room"""
    chatroom = await channel_service.get_chat_room(room_id)
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chat room không tồn tại")
    messages = await channel_service.get_messages(room_id, limit=1000)
    media = []
    for msg in messages:
        if msg.get("msg_type") in ["image", "video"] and msg.get("content"):
            media.append({
                "message_id": msg["message_id"],
                "type": msg["msg_type"],
                "file_id": msg["content"],
                "file_name": msg.get("file_name", ""),
                "sender_name": msg.get("sender_name", ""),
                "created_at": msg["created_at"].isoformat() if msg.get("created_at") else None
            })
    return {"media": media}

@router.get("/chatrooms/{room_id}/files")
async def get_room_files(room_id: str, current_user: dict = Depends(get_current_user)):
    """Lấy danh sách file tài liệu trong room (không bao gồm ảnh/video)"""
    chatroom = await channel_service.get_chat_room(room_id)
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chat room không tồn tại")
    messages = await channel_service.get_messages(room_id, limit=1000)
    files = []
    for msg in messages:
        if msg.get("msg_type") == "file" and msg.get("content"):
            files.append({
                "message_id": msg["message_id"],
                "file_id": msg["content"],
                "file_name": msg.get("file_name", "Tải file"),
                "sender_name": msg.get("sender_name", ""),
                "created_at": msg["created_at"].isoformat() if msg.get("created_at") else None
            })
    return {"files": files}

@router.get("/chatrooms/{room_id}/search")
async def search_messages(room_id: str, q: str, limit: int = 50, current_user: dict = Depends(get_current_user)):
    """Tìm kiếm tin nhắn theo từ khóa"""
    chatroom = await channel_service.get_chat_room(room_id)
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chat room không tồn tại")
    messages = await channel_service.search_messages(room_id, q, limit)
    return {"results": messages}

@router.get("/{channel_id}/rules")
async def get_channel_rules(channel_id: str, current_user: dict = Depends(get_current_user)):
    rules = await channel_service.get_channel_rules(channel_id)
    if not rules:
        return {"channel_id": channel_id, "enabled": False, "rules": []}
    return rules.model_dump()

@router.put("/{channel_id}/rules")
async def update_channel_rules(channel_id: str, req: dict, current_user: dict = Depends(get_current_user)):
    email = current_user["sub"]
    channel = await channel_service.get_channel(channel_id)
    if not channel or channel.owner_email != email:
        raise HTTPException(403, "Chỉ chủ kênh mới có quyền")
    from meeting.models.channel_model import ChannelRules
    rules = ChannelRules(
        channel_id=channel_id,
        enabled=req.get("enabled", False),
        rules_text=req.get("rules_text", ""),
        enabled_types=req.get("enabled_types", []),
        action=req.get("action", "warn"),
        max_violations=req.get("max_violations", 3),
        penalty_time=req.get("penalty_time"),
        updated_by=email
    )
    await channel_service.save_channel_rules(rules)
    return rules.model_dump()