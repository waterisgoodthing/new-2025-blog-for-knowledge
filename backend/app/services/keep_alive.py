import asyncio
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger("keep_alive")


async def _ping_loop(stop_event: asyncio.Event):
    settings = get_settings()
    interval = settings.KEEP_ALIVE_INTERVAL
    url = settings.KEEP_ALIVE_URL

    logger.info("Keep-alive started: %s every %ds", url, interval)

    async with httpx.AsyncClient(timeout=10) as client:
        while not stop_event.is_set():
            try:
                resp = await client.get(url)
                logger.debug("Keep-alive ping %s -> %d", url, resp.status_code)
            except Exception:
                logger.warning("Keep-alive ping failed", exc_info=True)

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
                break
            except asyncio.TimeoutError:
                pass

    logger.info("Keep-alive stopped")


def start_keep_alive() -> asyncio.Event:
    stop_event = asyncio.Event()
    asyncio.create_task(_ping_loop(stop_event))
    return stop_event


async def stop_keep_alive(stop_event: asyncio.Event):
    stop_event.set()
