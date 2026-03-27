import logging

import aiohttp

from config import BOT_TOKEN, DEV_LOG_TELEGRAM_ID

logger = logging.getLogger(__name__)


def _enabled() -> bool:
    return bool(BOT_TOKEN and DEV_LOG_TELEGRAM_ID)


async def send_dev_log(message: str) -> None:
    if not _enabled():
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": DEV_LOG_TELEGRAM_ID,
        "text": message[:4000],
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status >= 400:
                    body = await resp.text()
                    logger.warning("Developer log send failed: status=%s body=%s", resp.status, body)
    except Exception:
        logger.exception("Developer log send error")
