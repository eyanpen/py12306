import os
from typing import Final
from autoticket.data.constants import ConstMeta

class config(metaclass=ConstMeta):
    ROOT_DIR: Final[str]=".cache"
    AUTH_FILE: Final[str] = os.path.join(ROOT_DIR,"auth_state.json")
    DATA_FILE: Final[str] = os.path.join(ROOT_DIR,"sys_data.json")
    INDEX_HTML: Final[str] = "https://kyfw.12306.cn/otn/view/index.html"
    PASSENGERS_HTML: Final[str] = "https://kyfw.12306.cn/otn/view/passengers.html"

class selectors(metaclass=ConstMeta):
    """
    <div class="btn-area"><a style="margin-top: 12px;" href="javascript:" id="query_ticket" class="btn92s" shape="rect">查询</a>
</div>
    """
    # 精确选择器：带有 ID 的 a 标签
    query_btn_selector: Final[str] = "a#query_ticket"
