
import asyncio
import os
from playwright.async_api import async_playwright
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(CURRENT_DIR, "toolbar.html")
JS_FILE_PATH = os.path.join(CURRENT_DIR, "jscode.js")

async def station_data_changed(date_str):
    print(f"📅 [日期变动] 收到新日期: {date_str}")
    # 在这里执行你的业务逻辑，比如重新查询车票信息
    print(f"⚡ 正在根据 {date_str} 更新站点数据...")
# --- 这是你想要触发的 Python 本地函数 ---
async def passenger_is_changed(name, is_checked):
    status = "选中" if is_checked else "取消选中"
    print(f"\n🐍 [Python 回调] 收到信号！")
    print(f"👤 乘客姓名: {name}")
    print(f"✅ 当前状态: {status}")
    # 这里可以写你的业务逻辑，比如写入数据库或操作其他网页元素
    print("-" * 30)

async def inject_ui(page):

    # 1. 读取本地 HTML 文件内容
    if not os.path.exists(HTML_PATH):
        print(f"错误: 找不到文件 {HTML_PATH}")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        toolbar_content = f.read()
        with open(JS_FILE_PATH, 'r', encoding='utf-8') as jf:
            js_logic = jf.read()
        # 2. 注入到页面
            # 使用 Range().createContextualFragment 是为了强制执行 HTML 字符串中的 <script> 标签
            await page.evaluate(js_logic, toolbar_content)

async def handle_navigated(frame,page):
    # 只在主框架跳转时注入，忽略那些 iframe
    if frame == page.main_frame:
        print(f"主页面已跳转至: {frame.url}")
        await inject_ui(page)
async def inject_local_toolbar(page):
    # 1. 只需要调用一次，函数会一直跟着这个 page 对象
    await page.expose_function("pyPassengerChanged", passenger_is_changed)
    await page.expose_function("station_data_changed", station_data_changed)
    # 2. 监听跳转：每次页面加载完成，自动重新把 UI 贴上去
    page.on("framenavigated", lambda frame: asyncio.create_task(handle_navigated(frame,page)))
    # 初次加载
    await inject_ui(page)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 监听浏览器控制台输出
        page.on("console", lambda msg: print(f"来自页面的日志: {msg.text}"))
        
        # await page.goto("https://www.baidu.com")
        
        # 注入本地的 toolbar.html
        await inject_local_toolbar(page)
        
        print("工具栏注入完成。")
        await page.wait_for_event("close", timeout=0)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())