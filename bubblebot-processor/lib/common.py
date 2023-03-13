import httpx
from httpx import Timeout
from apscheduler.schedulers.asyncio import AsyncIOScheduler

httpx_timeout=Timeout(timeout=15.0)
httpx_client = httpx.AsyncClient(timeout=httpx_timeout)
scheduler = AsyncIOScheduler(timezone='Asia/Shanghai')
