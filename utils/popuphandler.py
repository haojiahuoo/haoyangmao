import uiautomator2 as u2
import time

class PopupHandler:
    def __init__(self, device):
        self.d = device
        self.common_popups = [
            {"name": "添加到主屏幕", "text": "取消"},
            # {"name": "权限请求", "text": "允许"},
            # {"name": "今日签到可领", "text": "立即签到"},
            # {"name": "广告弹窗", "text": "跳过"},
            # {"name": "系统提示", "text": "确定"},
            # {"name": "系统提示", "text": "点我可领"},
            # {"name": "翻倍任务开启", "text": "去看内容"}
        ]
    
    def check_and_handle_popup(self, timeout=3.0):
        """检查并处理常见弹窗（组合多种匹配策略）"""
        handled = False
        for popup in self.common_popups:
            # 定义多种匹配方式
            selectors = [
                self.d(textContains=popup["text"]),
                self.d(textMatches=f".*{popup['text']}.*"),
                self.d.xpath(f'//*[contains(@text, "{popup["text"]}")]')
            ]
            
            for selector in selectors:
                if selector.exists:
                    try:
                        selector.click()
                        print(f"✅ 已处理弹窗 [{popup['name']}] - 点击: {popup['text']}")
                        handled = True
                        time.sleep(1)
                        break  # 找到并处理后跳出当前循环
                    except Exception as e:
                        print(f"❌ 处理弹窗失败 [{popup['name']}]: {str(e)}")
                    break  # 找到元素后不再尝试其他匹配方式
        return handled

    def monitor_popups(self, interval=2.0):
        """持续监控弹窗（后台线程使用）"""
        while True:
            self.check_and_handle_popup()
            time.sleep(interval)


# # 启动后台线程运行监控
# monitor_thread = threading.Thread(
#     target=handler.monitor_popups,
#     daemon=True  # 设置为守护线程（主程序退出时自动结束）
# )
# monitor_thread.start()
      