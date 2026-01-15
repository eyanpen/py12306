from playwright.async_api import async_playwright
from autoticket.query.query import query_ticket
from autoticket.login.login import login_12306, saveCookie

async def select_passengers(page, names):
    """
    :param names: 姓名列表，例如 ["彭燕珑", "彭妤菲"]
    """
    for name in names:
        # 构造 XPath
        xpath = f"//ul[@id='normal_passenger_id']//li/label[text()='{name}']"
        
        try:
            passenger_label = page.locator(xpath)
            # 等待元素出现（防止页面加载延迟）
            await passenger_label.wait_for(state="visible", timeout=5000)
            
            # 点击 label 即可勾选对应的复选框
            await passenger_label.click(force=True)
            print(f"已勾选乘车人: {name}")
            
        except Exception as e:
            print(f"无法找到乘车人 {name}，请检查该人是否在常用联系人列表中。")
            return None
    
    return page



async def run_book():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await login_12306(browser=browser)
        if page:
            page = await query_ticket(page)
        if page:
            page = await select_passengers(page, ["蒋金玉", "彭天佑","彭小清"])
            # if page:
            #     page 
        else:
            print("some error.")
        print("等待页面关闭（最优雅的永久停顿，直到你手动关掉浏览器）")
        await saveCookie(page.context)
        await page.wait_for_event("close", timeout=0)
        await browser.close()