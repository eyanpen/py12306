import os
from playwright.async_api import async_playwright
from autoticket.data.config import config

import asyncio
# 状态保存的文件路径


async def task_login(page):
    scan_login_btn =await page.wait_for_selector("text=扫码登录", timeout=0)
    if scan_login_btn:
            print("找到扫码登录按钮，正在点击...")
            await scan_login_btn.click()
            print("请扫码登录按钮")
    else:
        print("没有找到扫码登录按钮")
async def task_index(page):
    await page.wait_for_selector("text=我的12306", timeout=5000)
    print("登录成功/已通过 Cookie 自动登录！")


async def smart_wait(page):
    # --- 关键修正：必须先创建任务对象 ---
    # 不要直接把函数名传给 wait，要传 Task
    t1 = asyncio.create_task(task_login(page))
    t2 = asyncio.create_task(task_index(page))

    # 谁先到就回传谁
    done, pending = await asyncio.wait(
        [t1, t2], 
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # 取消还没完成的任务
    for task in pending:
        task.cancel()
        
    # 获取最快任务的结果
    first_task = done.pop()
    print(f"检测到页面状态已确定：{first_task}")
    return page


async def login_12306(browser):
    
    # 1. 检查是否存在已保存的状态文件
    if os.path.exists(config.AUTH_FILE):
        print("检测到已存在的 Cookie，尝试免登录...")
        # 创建带有状态的上下文
        context = await browser.new_context(storage_state=config.AUTH_FILE)
    else:
        print("未发现状态文件，请手动扫码登录...")
        context = await browser.new_context()

    page = await context.new_page()
    await page.goto(config.INDEX_HTML)

    page=await smart_wait(page)
    while True: # 总超时 10 秒
        if "login.html" in page.url:
            # 如果在登录页，寻找按钮
            btn = page.locator(".login-code-main")
            if await btn.is_visible():
                print("成功切换到扫码登录界面！请扫描")
                # await page.wait_for_timeout(5000)
                # break
        elif "index.html" in page.url:
            print("检测到已在首页，跳过登录按钮等待")
            break
        await page.wait_for_timeout(500)
    await context.storage_state(path=config.AUTH_FILE)
    print(f"新的登录状态已保存至: {config.AUTH_FILE}")


    # 4. 继续你的业务逻辑（如下单、查票）
    print("当前页面标题:", await page.title())
    
    return page
async def saveCookie(context):
    await context.storage_state(path=config.AUTH_FILE)
    print(f"新的登录状态已保存至: {config.AUTH_FILE}")
async def run_12306():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await login_12306(browser=browser)
        await page.wait_for_timeout(10000)
        await browser.close()
if __name__ == "__main__":
    asyncio.run(run_12306())