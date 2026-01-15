
from datetime import datetime
from playwright.async_api import async_playwright
import asyncio
from autoticket.query.query import goto_query_page

class PageKeeper:
    def __init__(self, page, refresh_interval=60):
        """
        page: Playwright page 对象
        refresh_interval: 自动刷新间隔（秒）默认一分钟
        """
        self.page = page
        self.refresh_interval = refresh_interval
        self._refresh_task = None
        self._last_refresh = None
        self._lock = asyncio.Lock()


    async def start(self):
        """启动定时刷新任务"""
        if self._refresh_task is None or self._refresh_task.done():
            self._refresh_task = asyncio.create_task(self._refresh_loop())

    async def stop(self):
        """停止刷新任务"""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except BaseException as e:
                print("停止失败",e)
                pass
            self._refresh_task = None

    async def _refresh_loop(self):
        await goto_query_page(self.page)
        while True:
            async with self._lock:
                now = datetime.now()
                # 如果上次刷新时间 < refresh_interval，不刷新，重置定时器
                if self._last_refresh and (now - self._last_refresh).total_seconds() < self.refresh_interval:
                    wait_time = self.refresh_interval - (now - self._last_refresh).total_seconds()
                    await asyncio.sleep(wait_time)
                    continue

                try:
                    print(f"[{datetime.now()}] Refreshing page to keep login alive...")
                    await self.page.evaluate("fetch('/heartbeat')")  # 示例
                    self._last_refresh = datetime.now()
                except Exception as e:
                    print(f"Refresh failed: {e}")

            await asyncio.sleep(self.refresh_interval)

    async def reset_timer(self):
        """外部触发刷新后重置定时器"""
        async with self._lock:
            self._last_refresh = datetime.now()
            print(f"[{datetime.now()}] Refresh timer reset by external action.")