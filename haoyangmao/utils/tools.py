import time
import uiautomator2 as u2
from typing import Union

def click_by_xpath_text(
    d: u2.Device,
    texts: Union[str, list[str]],  # 支持 str 或 list[str]
    timeout: float = 10.0,
    raise_error: bool = False,
    log_prefix: str = ""
) -> bool:
    """
    通过 XPath 点击匹配任意一个文本的元素（支持单文本或多文本的"或"逻辑）
    :param d: uiautomator2 Device 对象
    :param texts: 要匹配的文本（字符串或字符串列表）
    :param timeout: 超时时间（秒）
    :param raise_error: 是否在失败时抛出异常
    :param log_prefix: 日志前缀
    :return: 是否点击成功
    """
    # 统一转成列表处理
    texts_list = [texts] if isinstance(texts, str) else texts
    xpath_conditions = " or ".join([f'contains(@text, "{t}")' for t in texts_list])
    selector = d.xpath(f"//*[{xpath_conditions}]")
    
    try:
        if selector.wait(timeout=timeout):
            selector.click()
            print(f"{log_prefix}[成功] 点击: {texts_list}")  # 改为 texts_list
            return True
        else:
            print(f"{log_prefix}[失败] 未找到: {texts_list}")  # 改为 texts_list
            if raise_error:
                raise TimeoutError(f"未找到文本: {texts_list}")  # 改为 texts_list
            return False
    except Exception as e:
        print(f"{log_prefix}[异常] 错误: {e}")
        if raise_error:
            raise
        return False


def wait_exists(selector, timeout=5, interval=0.5) -> bool:
    """
    快速判断 selector 是否在指定时间内存在，避免长时间阻塞。
    
    :param selector: uiautomator2 控件选择器
    :param timeout: 最多等待的秒数
    :param interval: 每次检查间隔时间
    :return: 出现返回 True，否则 False
    """
    elapsed = 0
    while elapsed < timeout:
        try:
            if selector.info:
                return True
        except:
            pass
        time.sleep(interval)
        elapsed += interval
    return False
