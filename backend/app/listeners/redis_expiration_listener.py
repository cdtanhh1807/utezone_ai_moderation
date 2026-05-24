import asyncio
from core.redis import redis_client
from services.other.ban_service import on_ban_expired

async def handle_ban_expire_event(key: str):
    # format: ban_expire:email:violationId
    _, violatorEmail, violationId = key.split(":")

    print(f"🔔 Redis event: ban expired for {violatorEmail}")
    await on_ban_expired(violatorEmail, violationId)


async def redis_expiration_listener():
    print("🚀 Starting Redis expiration listener...")

    pubsub = redis_client.pubsub()

    # lắng nghe sự kiện expired
    await pubsub.psubscribe("__keyevent@0__:expired")

    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            key = message["data"]

            if key.startswith("ban_expire:"):
                await handle_ban_expire_event(key)
