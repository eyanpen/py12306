from playwright.async_api import async_playwright
from autoticket.login.login import login_12306, saveCookie
async def input_station_direct(page, fromStationText, fromStation, station_name, station_code):
    """
    直接通过 JS 设置值，跳过 UI 模拟
    station_code 示例: 北京是 'BJP', 上海是 'SHH'
    """
   # 1. 首先确保 ID 为 fromStationText 的元素已经出现在页面上
    # 这是防止 "null" 错误的关键
    try:
        await page.wait_for_selector(f"#{fromStationText}", state="attached", timeout=5000)
        
        # 2. 执行 JS，并在 JS 内部做一层判断
        await page.evaluate(f"""
            () => {{
                const textInput = document.getElementById('{fromStationText}');
                const hiddenInput = document.getElementById('{fromStation}');
                
                if (textInput && hiddenInput) {{
                    textInput.value = '{station_name}';
                    hiddenInput.value = '{station_code}';
                    // 触发事件通知网页数据已更新
                    textInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    textInput.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                }} else {{
                    // 如果还是没找到，抛出一个清晰的错误给 Python
                    throw new Error("无法在当前页面找到 ID 为 fromStationText 或 fromStation 的元素");
                }}
            }}
        """)
        print(f"成功设置站点: {station_name} ({station_code})")
        
    except Exception as e:
        print(f"设置站点失败: {e}")
async def input_value(page, id_selector, value):
    # 1. 定位并点击，确保获得焦点
    from_input = page.locator(f"#{id_selector}")
    await from_input.click()
    
    # 2. 清空已有内容 (手动模拟：全选+退格)
    # await from_input.press("Control+A")
    # await from_input.press("Backspace")
    await from_input.type("s", delay=100)
    # 2. 强制等待 0.5 秒，让它的建议列表窗口弹出来并稳定
    await page.wait_for_timeout(500) 
    # 3. 继续输入剩下的
    await from_input.type("hanghai", delay=200)
    # 3. 模拟真实打字（设置 delay 让它看起来更像真人）
    # 这会触发 12306 的补全下拉列表
    # for char in "shanghai":
    #     await from_input.press(char)
    #     await page.wait_for_timeout(1000) # 手动控制节奏
    
    # 4. 关键步：等待下拉建议框出现，并按回车选中第一个
    # 12306 的建议框通常是 #panel_cities
    await page.wait_for_selector("#panel_cities", state="visible")
    await from_input.press("Enter")
    
    print(f"站点 {value} 输入完成")
# <input autocomplete="off" type="text" id="fromStationText" class="inp-txt" value="" name="leftTicketDTO.from_station_name">
async def input_value_simple(page, id, value):
    # 1. 定位到出发地输入框并点击
    from_input = page.locator(f"#{id}")
    await from_input.click()
    
    # 2. 清空并输入城市名
    await from_input.fill(value) # 确保清空
async def query_ticket(page):
    querybtn =await page.wait_for_selector("text=车票预订", timeout=0)
    if querybtn:
        try:
            await querybtn.click()
            await input_station_direct(page,"fromStationText", "fromStation", "上海", station_code="SHH")
            await input_station_direct(page,"toStationText", "toStation", "衡阳", station_code="HYQ")
            await set_12306_date(page,"2026-01-20")
            await click_query(page)
            trains = await get_all_train_numbers(page)
            # await show_train_state(page, trains)
            for train in trains:
                if train.startswith(("T", "K")):
                    print("以 T 或 K 开头", train)
                    page = await book_train(page,train)
                    if page:
                        return page
                    else:
                        print("try other one.")
                else:
                    print("跳过贵的车次", train)
            # await input_value_simple(page,"fromStationText","上海")
            # await input_value(page,"fromStationText","上海")
        except any as e:
            print(e)
    
    return None
async def set_12306_date(page, target_date):
    """
    <div class="inp-w" style="z-index:1200">
    <input aria-label="请输入日期，例如2021杠01杠01" autocomplete="off" type="text" class="inp_selected" name="leftTicketDTO.train_date"
            id="train_date" value="2013-06-07 周五">
    <span id="date_icon_1" class="i-date"></span>
    </div>

    精确锁定 input 类型的 train_date 并设置日期
    :param target_date: "2026-01-20"
    """
    # 使用 CSS 选择器确保只匹配 input 标签
    selector = "input#train_date"
    
    # 执行前先确保该 input 已经加载
    try:
        await page.wait_for_selector(selector, state="attached", timeout=5000)
        
        await page.evaluate(f"""
            () => {{
                // 使用 querySelector 精确匹配 input 标签且 ID 为 train_date
                const el = document.querySelector('{selector}');
                
                if (el && el.tagName === 'INPUT') {{
                    // 1. 强行移除只读属性
                    el.removeAttribute('readonly');
                    
                    // 2. 写入新值
                    el.value = '{target_date}';
                    
                    // 3. 模拟真实的浏览器事件流
                    // 必须触发这些事件，12306 的内部 JS 框架才会接收到新日期
                    const events = ['input', 'change', 'blur'];
                    events.forEach(evtName => {{
                        el.dispatchEvent(new Event(evtName, {{ bubbles: true }}));
                    }});
                    
                    return true;
                }}
                return false;
            }}
        """)
        print(f"成功将日期设置为: {target_date}")
        
    except Exception as e:
        print(f"设置日期失败，错误信息: {e}")

async def click_query(page):
    """
    点击查询按钮并等待列表刷新
    <div class="btn-area"><a style="margin-top: 12px;" href="javascript:" id="query_ticket" class="btn92s" shape="rect">查询</a>
</div>
    """
    # 精确选择器：带有 ID 的 a 标签
    query_btn_selector = "a#query_ticket"
    
    try:
        # 1. 等待按钮进入 DOM 且可见
        btn = page.locator(query_btn_selector)
        await btn.wait_for(state="visible", timeout=5000)
        print("查询按钮可见")
        # 2. 滚动到按钮位置（防止被底部页脚遮挡）
        await btn.scroll_into_view_if_needed()
        
        # 3. 执行点击
        print("正在点击查询按钮...")
        # force=True 会跳过 Playwright 的交互性检查（即不管有没有遮罩层遮挡，直接点）
        await btn.click(force=True)
        print("已强制点击查询按钮")        
        # 4. 关键：等待“加载中”遮罩层消失，或者等待表格出现
        # 12306 查询时通常会出现一个透明或半透明的 loading 提示
        # 我们等待车票列表容器加载出内容
        await page.wait_for_selector("#t-list", state="visible", timeout=10000)
        print("查询成功，车票列表已更新。")
        
    except Exception as e:
        print(f"点击查询失败或加载超时: {e}")
        # 如果点击没反应，可以尝试用 JS 强行触发
        print("尝试使用 JS 强制触发查询...")
        await page.evaluate("document.getElementById('query_ticket').click()")
async def get_all_train_numbers(page):
    
    # 定位所有带有 datatran 属性的 tr 标签
    selector = "tr[datatran]"
    await page.wait_for_selector(selector, timeout=10000, state="attached")

    # 在浏览器中执行一段 JS，直接提取所有 datatran 属性
    train_numbers = await page.locator(selector).evaluate_all(
        "(elements) => elements.map(el => el.getAttribute('datatran'))"
    )
    print(f"共发现RAW {len(train_numbers)} 个车次: {train_numbers}")
    # 过滤掉可能存在的空值
    train_numbers = [t for t in train_numbers if t]
    
    print(f"共发现 {len(train_numbers)} 个车次: {train_numbers}")
    return train_numbers

def get_xpath_for_orderable(train_number):
    train_row_xpath = f"//tr[.//a[text()='{train_number}']]"
    return f"{train_row_xpath}//a[text()='预订']"

async def show_train_state(page, trains):
    """
    根据车次号预订车次
    :param trains: 车次字符串，如 "G102","K11"
    """
    for  train_number in trains:
        print(f"正在寻找车次: {train_number} ...")
        book_button_xpath = get_xpath_for_orderable(train_number=train_number)

        try:
            btn = page.locator(book_button_xpath)
            
            if await btn.is_visible(timeout=100):
                print(f"车次 {train_number} 可订")
            else:
                print(f"页面上车次 {train_number} 不可订")
                
        except Exception as e:
            print(f"预订操作异常: {e}")
        


async def book_train(page, train_number):
    """
    根据车次号预订车次
    :param train_number: 车次字符串，如 "G102"
    """
    print(f"正在寻找车次: {train_number} ...")
    
    book_button_xpath = get_xpath_for_orderable(train_number=train_number)

    try:
        # 2. 等待该行的预订按钮出现
        # 注意：如果票卖完了，按钮可能是灰色的（不可点击）
        btn = page.locator(book_button_xpath)
        
        if await btn.is_visible(timeout=100):
            # 检查按钮是否为“不可预订”状态（通常会有特殊的 class）
            print(f"发现 {train_number} 有票，正在点击预订...")
            await btn.click(force=True)
            # 预订后会跳转到乘客选择页
            await page.wait_for_url("**/confirmPassenger/**", timeout=10000)
            print("成功进入订单确认页面")
            return page
        else:
            print(f"页面上未找到车次 {train_number}")
            
    except Exception as e:
        print(f"预订操作异常: {e}")
    
    return None

async def run_query():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await login_12306(browser=browser)
        await query_ticket(page)

        print("等待页面关闭（最优雅的永久停顿，直到你手动关掉浏览器）")
        await saveCookie(page.context)
        await page.wait_for_event("close", timeout=0)
        await browser.close()
