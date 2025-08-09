import time
import uiautomator2 as u2
from typing import Union

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
    点击匹配条件的元素（支持文本匹配、额外属性、或直接传 XPath）。
    优先点击可点击节点，如果没有就坐标点击，并打印点击的节点信息。

    :return: 是否点击成功
    """
    # 构造选择器
    if xpaths:
        xpath_list = [xpaths] if isinstance(xpaths, str) else xpaths
        xpath_conditions = " | ".join(xpath_list)
        selector = d.xpath(xpath_conditions)
    else:
        # 文本条件
        text_conditions = []
        if texts:
            texts_list = [texts] if isinstance(texts, str) else texts
            text_conditions = [f'contains(@text, "{t}")' for t in texts_list]

        # 属性条件
        attr_conditions = []
        for k, v in attrs.items():
            attr_name = {
                "className": "class",
                "resourceId": "resource-id",
                "contentDesc": "content-desc"
            }.get(k, k)
            attr_conditions.append(f'@{attr_name}="{v}"')

        # 合并条件
        all_conditions = []
        if text_conditions:
            all_conditions.append("(" + " or ".join(text_conditions) + ")")
        if attr_conditions:
            all_conditions.extend(attr_conditions)

        xpath_query = "//*"
        if all_conditions:
            xpath_query += "[" + " and ".join(all_conditions) + "]"
        selector = d.xpath(xpath_query)

    try:
        # 等待元素出现
        if selector.wait(timeout=timeout):
            nodes = selector.all()
            if not nodes:
                print(f"{log_prefix}[失败] 未找到元素节点")
                return False

            # 优先点击可点击节点
            for n in nodes:
                if n.info.get('clickable', False):
                    n.click()
                    print(f"{log_prefix}✅ 点击可点击节点: {n.info}")
                    if wait_gone:
                        if selector.wait_gone(timeout=timeout):
                            return True
                    else:
                        return True

            # 如果都不可点击，用坐标点击第一个
            bounds = nodes[0].info.get("bounds")
            if bounds:
                x = (bounds['left'] + bounds['right']) // 2
                y = (bounds['top'] + bounds['bottom']) // 2
                d.click(x, y)
                print(f"{log_prefix}⚠️ 坐标点击节点: {nodes[0].info}")
                if wait_gone:
                    if selector.wait_gone(timeout=timeout):
                        return True
                else:
                    return True

            print(f"{log_prefix}❌ 找到元素但无法点击: {nodes[0].info}")
            return False
        else:
            print(f"{log_prefix}[失败] 未找到匹配的元素")
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
