import asyncio
import logging
from core.redis import redis_client, delete_ban_countdown
from dto.account.request.update_account_request import UpdateAccountRequest
from repositories.ban_repository import BanRepository
from services.impls.account_service_impl import AccountServiceImpl
from models.account_model import Permission

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("perm_watcher")

ACTIONS = ["post", "comment", "message"]   # thứ tự bit 0,1,2

async def restore_permission(email: str, action: str):
    """Trả quyền đã hết hạn về DB."""
    try:
        service = AccountServiceImpl()
        acc = await service.get_account_by_email(email)
        if not acc:
            return
        per_list = list(acc.permission.pernum)
        idx = ACTIONS.index(action)
        per_list[idx] = '1'
        new_pernum = ''.join(per_list)

        await service.update(
            UpdateAccountRequest(
                id=str(acc.id),
                permission=Permission(
                    pernum=new_pernum,
                    validity=acc.permission.validity
                )
            )
        )
        repo = await BanRepository.remove_expired_violations(email)
        logger.info("[PERM] Trả quyền %s cho %s", action, email)
    except Exception as e:
        logger.exception("restore_permission %s %s: %s", email, action, e)

SCAN_PATTERN = "ban:*"
SLEEP_SECONDS = 0.2   # 200 ms

async def permission_watcher_loop():
    """Vòng lặp background: KEYS -> TTL từng key -> xử lý ttl=-2."""
    while True:
        try:
            keys = await redis_client.keys(SCAN_PATTERN)
            for key in keys:
                ttl = await redis_client.ttl(key)
                # logger.info("[PERM] scan key=%s ttl=%s", key, ttl)
                if ttl <= 0:          # <-- thay điều kiện này
                    _, email, action = key.split(":")
                    # logger.info("[PERM] Detected expired key %s", key)
                    await restore_permission(email, action)
                    await delete_ban_countdown(email, action)
        except Exception as e:
            logger.exception("permission_watcher: %s", e)
        await asyncio.sleep(SLEEP_SECONDS)