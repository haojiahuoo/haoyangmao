import time
import uiautomator2 as u2
from typing import Union

from typing import Union
import uiautomator2 as u2

def click_by_xpath_text(
    d: u2.Device,
    texts: Union[str, list[str], None] = None,  # 要匹配的文本，可为 None
    timeout: float = 10.0,
    wait_gone: bool = True,
    raise_error: bool = False,
    log_prefix: str = "",
    xpaths: Union[str, list[str], None] = None,  # 直接传 XPath
    **attrs  # 额外的控件属性，如 className="xxx", resourceId="xxx"
) -> bool:
    """
    点击匹配条件的元素（支持文本匹配、额外属性、或直接传 XPath）
    
    :param d: uiautomator2 Device 对象
    :param texts: 要匹配的文本（字符串、字符串列表，或 None）
    :param timeout: 超时时间（秒）
    :param wait_gone: 点击后是否等待元素消失
    :param raise_error: 是否在失败时抛出异常
    :param log_prefix: 日志前缀
    :param xpaths: 直接传 XPath 字符串或列表（优先级最高）
    :param attrs: 其他控件属性（className=..., resourceId=... 等）
    :return: 是否点击成功
    """
    
    # 构造选择器
    if xpaths:  
        # 如果直接传了 XPath
        xpath_list = [xpaths] if isinstance(xpaths, str) else xpaths
        xpath_conditions = " | ".join(xpath_list)  # 多个 XPath 用 “或” 连接
        selector = d.xpath(xpath_conditions)

    else:
        # 文本条件
        text_conditions = []
        if texts:
            texts_list = [texts] if isinstance(texts, str) else texts
            text_conditions = [f'contains(@text, "{t}")' for t in texts_list]
        
        # 额外属性条件
        attr_conditions = []
        for k, v in attrs.items():
            # uiautomator2 属性名转 XPath 属性名
            # 比如 className -> @class, resourceId -> @resource-id
            attr_name = {
                "className": "class",
                "resourceId": "resource-id",
                "contentDesc": "content-desc"
            }.get(k, k)  # 如果不在映射表中就原样用
            attr_conditions.append(f'@{attr_name}="{v}"')

        # 合并条件（用 and/or 组合）
        all_conditions = []
        if text_conditions:
            all_conditions.append("(" + " or ".join(text_conditions) + ")")
        if attr_conditions:
            all_conditions.extend(attr_conditions)  # 属性是 and 关系

        xpath_query = "//*"
        if all_conditions:
            xpath_query += "[" + " and ".join(all_conditions) + "]"

        selector = d.xpath(xpath_query)

    # 点击逻辑
    try:
        if selector.wait(timeout=timeout):
            selector.click()
            print("第一次点击")
            if wait_gone:
                if selector.wait_gone(timeout=timeout):
                    print(f"{log_prefix}[点击成功]")
                    return True
                else:
                    selector.click()
                    print("第二次点击")
                    if selector.wait_gone(timeout=timeout):
                        print(f"{log_prefix}[点击成功]")
                        return True
                    else:
                        print(f"{log_prefix} 点击失败 [元素未消失]")
            else:
                print(f"{log_prefix}元素不会消失 [点击成功]")
                return True
        else:
            print(f"{log_prefix}[失败] 未找到元素")
            if raise_error:
                raise TimeoutError(f"未找到匹配的元素")
            return False
    except Exception as e:
        print(f"{log_prefix}[异常] 错误: {e}")
        if raise_error:
            raise
        return False



def wait_exists(selector, timeout=3, interval=0.2) -> bool:
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
            if selector.info:  # 立即返回，不等待
                return True
        except:
            pass
        time.sleep(interval)
        elapsed += interval
    return False
