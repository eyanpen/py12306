from autoticket.book.book import run_book
import traceback
import asyncio
from playwright.async_api import async_playwright
from autoticket.query.query import query_ticket
from autoticket.login.login import login_12306, saveCookie
from autoticket.query.passengers import get_all_passengers
from autoticket.data.data import sysdata

async def run_steps(page, steps):
    num=0
    for step in steps:
        num+=1
        step_name = getattr(step, "__name__", repr(step))
        print(f"执行第{num}步{step_name}")
        try:
            page = await step(page)
            if not page:
                print(f"执行第{num}步{step_name}出错. 停止执行其余步骤。");
                return
        except BaseException as e:
            print(f"执行第{num}步{step_name}出错:", e)
            traceback.print_exc()
    print(f"完成所有步骤:{num}步")
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await login_12306(browser)
        await run_steps(page=page,steps=[get_all_passengers, query_ticket])

        print("等待页面关闭（最优雅的永久停顿，直到你手动关掉浏览器）")
        await saveCookie(page.context)
        sysdata.saveToFile()
        await page.wait_for_event("close", timeout=0)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())