
// js_code.js
(async (htmlContent) => {
    const inject = () => {
        // 1. 幂等性检查：如果已经存在则不再注入
        if (document.getElementById('right-toolbar-autoticket')) return;

        // 2. 检查 body 是否准备好
        if (!document.body) {
            setTimeout(inject, 50); // 每50ms重试一次
            console.log("body 还没准备好")
            return;
        }

        // 3. 创建并注入容器
        const container = document.createElement('div');
        container.id = 'right-toolbar-wrapper-autoticket';
        container.innerHTML = htmlContent;
        document.body.appendChild(container);
        console.log("Toolbar injected successfully.");
         // JavaScript 逻辑更新
        window.toggleToolbar = () => {
            const el = document.getElementById('right-toolbar-autoticket');
            if (el) el.classList.toggle('collapsed-autoticket');
        };

        window.handleDateChange = async (dateValue) => {
            console.log(`[JS] 日期变动: ${dateValue}`);
            if (window.station_data_changed) {
                await window.station_data_changed(dateValue);
            }
        };

        // 初始化日期
        const today_autoticket = new Date().toISOString().split('T')[0];
        const dateInput = document.getElementById('travel-date-autoticket');
        if (dateInput) dateInput.value = today_autoticket;

        (function initToolbarAutoticket() {
            // 使用更具体的 ID 选择器防止冲突
            const inputs = document.querySelectorAll('#user-list-autoticket input');
            inputs.forEach(input => {
                input.addEventListener('change', async (e) => {
                    const name = e.target.value;
                    const isChecked = e.target.checked;
                    
                    console.log(`[JS] 触发勾选: ${name} -> ${isChecked}`);

                    if (window.pyPassengerChanged) {
                        await window.pyPassengerChanged(name, isChecked);
                    }
                });
            });
        })();
    };

    inject();
})