from playwright.async_api import async_playwright

async def get_all_passengers(page):
    passengersUrl="https://kyfw.12306.cn/otn/view/passengers.html"
    if "passengers" not in page.url:
        print("跳转",page.url, "到",passengersUrl)
        await page.goto(passengersUrl)
    passengers = await page.locator("td.br-none > div.name-yichu").all_inner_texts()
    print(passengers)
    return  passengers


