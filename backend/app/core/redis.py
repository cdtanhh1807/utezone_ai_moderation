from datetime import datetime, timezone
import json
import os
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

FEED_TTL = 600          # cache feed 10 phút
VIEWED_TTL = 7 * 24 * 3600  # lưu viewed 7 ngày

async def set_otp(email: str, otp: str, expire: int):
    await redis_client.set(f"otp:{email}", otp, ex=expire)

async def get_otp(email: str):
    return await redis_client.get(f"otp:{email}")

async def delete_otp(email: str):
    await redis_client.delete(f"otp:{email}")

async def blacklist_token(token: str, ttl: int):
    await redis_client.set(f"blacklist:{token}", "true", ex=ttl)

async def is_token_blacklisted(token: str) -> bool:
    result = await redis_client.get(f"blacklist:{token}")
    return result == "true"

# async def cache_feed(email: str, data: list[dict], ttl: int = FEED_TTL):
#     await redis_client.set(f"feed:{email}", json.dumps(data, default=str), ex=ttl)

# async def get_cached_feed(email: str) -> list[dict] | None:
#     raw = await redis_client.get(f"feed:{email}")
#     return json.loads(raw) if raw else None

# async def invalidate_feed_cache(email: str):
#     await redis_client.delete(f"feed:{email}")

# async def mark_post_viewed(email: str, post_id: str):
#     key = f"viewed:{email}"
#     await redis_client.sadd(key, post_id)
#     await redis_client.expire(key, 7 * 24 * 3600)

# async def get_viewed_posts(email: str) -> set[str]:
#     return await redis_client.smembers(f"viewed:{email}")
async def cache_feed(email: str, data: list[dict], ttl: int = FEED_TTL):
    await redis_client.set(f"feed:{email}", json.dumps(data, default=str), ex=ttl)


async def get_cached_feed(email: str) -> list[dict] | None:
    raw = await redis_client.get(f"feed:{email}")
    return json.loads(raw) if raw else None


async def invalidate_feed_cache(email: str):
    await redis_client.delete(f"feed:{email}")


async def mark_post_viewed(email: str, post_id: str):
    key = f"viewed:{email}"
    await redis_client.sadd(key, post_id)
    await redis_client.expire(key, VIEWED_TTL)


async def get_viewed_posts(email: str) -> set[str]:
    return await redis_client.smembers(f"viewed:{email}")


async def reset_viewed_posts(email: str):
    await redis_client.delete(f"viewed:{email}")

#ban
async def set_ban_countdown(email: str, action: str, seconds: int):
    """Set bộ đếm ngược cho 1 quyền cụ thể"""
    print("Bat dau dem nguoc")
    await redis_client.set(f"ban:{email}:{action}", "1", ex=seconds)

async def get_ban_countdown_seconds(email: str, action: str) -> int:
    """Số giây còn lại; 0 nghĩa là đã hết"""
    ttl = await redis_client.ttl(f"ban:{email}:{action}")
    return max(ttl, 0)

async def delete_ban_countdown(email: str, action: str):
    """Xóa key (dùng khi admin gỡ thủ công)"""
    await redis_client.delete(f"ban:{email}:{action}")