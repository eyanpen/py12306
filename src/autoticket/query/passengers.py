from playwright.async_api import async_playwright
from autoticket.data.config import config
from autoticket.data.data import sysdata

async def get_all_passengers(page):
    if not page.url.startswith(config.PASSENGERS_HTML):
        print("跳转",page.url, "到", config.PASSENGERS_HTML)
        await page.goto(config.PASSENGERS_HTML)
    sysdata.passengers = await page.locator("td.br-none > div.name-yichu").all_inner_texts()
    print(sysdata.passengers)
    return  page


