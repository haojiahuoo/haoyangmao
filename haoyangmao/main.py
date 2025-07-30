import uiautomator2 as u2
import time, threading, random, math
from typing import Optional, Union, Callable, Any
from utils.popuphandler import PopupHandler
from utils.smart_swipe import SmartSwipe
from utils.ad_watcher import AdWatcher

def click_by_xpath_text(
    d: u2.Device,
    text: str,
    timeout: float = 10.0,
    raise_error: bool = False,
    log_prefix: str = ""
) -> bool:
    """
    通过 XPath 模糊匹配文本点击元素
    """
    selector = d.xpath(f'//*[contains(@text, "{text}")]')
    try:
        if selector.wait(timeout=timeout):
            selector.click()
            print(f"{log_prefix}[成功] 点击: '{text}'")
            return True
        else:
            print(f"{log_prefix}[失败] 未找到: '{text}'")
            if raise_error:
                raise TimeoutError(f"未找到文本: '{text}'")
            return False
    except Exception as e:
        print(f"{log_prefix}[异常] 错误: {e}")
        if raise_error:
            raise
        return False

def wait_until(
    condition: Union[Callable[[], bool], Any],
    timeout: float = 5,
    interval: float = 0.1
) -> bool:
    """
    通用等待函数（返回 bool）
    """
    elapsed = 0
    while elapsed < timeout:
        if callable(condition):
            if condition():
                return True
        elif hasattr(condition, 'exists'):  # 处理 u2 选择器
            if condition.exists:
                return True
        time.sleep(interval)
        elapsed += interval
    return False


if __name__ == "__main__":
    
    d = u2.connect("A3KUVB2428008483")# A3KUVB2428008483
    handler = PopupHandler(d)
    swipe = SmartSwipe(d)
    watcher = AdWatcher(d)

    # 启动后台线程运行监控
    monitor_thread = threading.Thread(
        target=handler.monitor_popups,
        daemon=True  # 设置为守护线程（主程序退出时自动结束）
    )
    # monitor_thread.start()
    

    def Start_working(apps):
        """开始工作"""
        for name, app in apps:
            if name == "快手极速版":
                # try:
                d.app_start(app)
                time.sleep(5)
                click_by_xpath_text(d, "去赚钱")
                time.sleep(5)

                if click_by_xpath_text(d, "点可领"):
                    watcher.watch_ad() 

                click_by_xpath_text(d, "看广告得金币")
                if wait_until(d.xpath('//*[contains(@text, "休息一下")]'), timeout=2):
                    print("广告冷却中，等待中...")
                else:
                    watcher.watch_ad()
                # finally:
                #     d.app_stop(app)
        
    apps = [
        ("快手极速版", "com.kuaishou.nebula"),
        ("抖音极速版", "com.ss.android.ugc.aweme.lite"),
        ("西瓜视频", "com.ss.android.ugc.aweme.xigua"),
        ("火山小视频", "com.ss.android.ugc.boom"),
        ("全民小视频", "com.ss.android.ugc.qmvideo"),
    ]
    Start_working(apps)