# from .account_service import restore_permission

async def on_ban_expired(violatorEmail: str, violationId: str):
    print(f"[BanService] Ban expired for {violatorEmail} (violation: {violationId})")

    # Xử lý business logic
    # await restore_permission(email)

    # Nếu bạn muốn log hoặc gửi email, thêm ở đây
