import time
import random
import math
from typing import Optional, Callable
import uiautomator2 as u2
from typing import Tuple, Union
from logger import log, log_error, log_debug

class SmartSwipe:
    def __init__(self, d: u2.Device):
        """
        初始化智能滑动工具
        
        Args:
            d (u2.Device): uiautomator2设备实例
        """
        self.d = d
        self.width, self.height = self.d.window_size()  # 获取屏幕尺寸

    def smart_swipe(self, direction="up", duration_min=0.3, duration_max=0.6, 
                   deviation_angle=15, random_offset=True):
        """
        增强版智能滑动方法（带坐标随机性和偏移度）
        
        Args:
            direction: 滑动方向 ('up', 'down', 'left', 'right')
            duration_min: 最小滑动持续时间(秒)
            duration_max: 最大滑动持续时间(秒)
            deviation_angle: 最大偏移角度(度)，默认15度
            random_offset: 是否启用随机偏移，默认True
        """
        # 计算滑动持续时间
        duration = random.uniform(duration_min, duration_max)
        
        # 基础滑动方向向量
        if direction == "up":
            base_vec = (0, -1)  # 向上
        elif direction == "down":
            base_vec = (0, 1)   # 向下
        elif direction == "left":
            base_vec = (-1, 0)  # 向左
        elif direction == "right":
            base_vec = (1, 0)   # 向右
        else:
            raise ValueError("direction must be 'up', 'down', 'left' or 'right'")
        
        # 计算滑动距离（屏幕尺寸的60%）
        swipe_distance = int(min(self.width, self.height) * 0.6)
        
        # 基础起点（屏幕中央区域）
        base_start_x = random.randint(int(self.width * 0.3), int(self.width * 0.7))
        base_start_y = random.randint(int(self.height * 0.3), int(self.height * 0.7))
        
        if random_offset:
            # 添加随机偏移角度
            angle_rad = math.radians(random.uniform(-deviation_angle, deviation_angle))
            cos_val = math.cos(angle_rad)
            sin_val = math.sin(angle_rad)
            
            # 计算带角度的方向向量
            dir_x = base_vec[0] * cos_val - base_vec[1] * sin_val
            dir_y = base_vec[0] * sin_val + base_vec[1] * cos_val
            
            # 计算终点坐标
            end_x = base_start_x + int(dir_x * swipe_distance)
            end_y = base_start_y + int(dir_y * swipe_distance)
        else:
            # 无随机偏移的标准滑动
            end_x = base_start_x + base_vec[0] * swipe_distance
            end_y = base_start_y + base_vec[1] * swipe_distance
        
        # 添加微小随机扰动
        start_x = base_start_x + random.randint(-10, 10)
        start_y = base_start_y + random.randint(-10, 10)
        end_x += random.randint(-5, 5)
        end_y += random.randint(-5, 5)
        
        # 确保坐标在屏幕范围内
        start_x = max(0, min(self.width - 1, start_x))
        start_y = max(0, min(self.height - 1, start_y))
        end_x = max(0, min(self.width - 1, end_x))
        end_y = max(0, min(self.height - 1, end_y))
        
        # 执行滑动
        self.d.swipe(start_x, start_y, end_x, end_y, duration)


    def click_by_xpath_text_with_swipe(self, text: str, max_swipes: int = 5, 
                                     swipe_duration: float = 0.5, wait_time: float = 1.0) -> bool:
        """
        增强版：通过文本点击元素，带滑动查找和智能等待
        
        Args:
            text: 要查找的文本内容
            max_swipes: 最大滑动次数
            swipe_duration: 每次滑动的持续时间(秒)
            wait_time: 每次滑动后的等待时间(秒)
            
        Returns:
            bool: 是否成功点击
        """
        xpath = f'//*[contains(@text, "{text}")]'
        
        for attempt in range(max_swipes + 1):
            time.sleep(0.5)  # 每次尝试前的固定等待
            
            try:
                element = self.d.xpath(xpath)
                if element.exists:
                    element_info = element.info
                    if not element_info:
                        log(f"⚠️ 找到元素但无法获取信息: {text}")
                        continue
                    
                    # 检查元素是否在屏幕上可见
                    bounds = element_info.get('bounds', {})
                    if bounds:
                        if (bounds['left'] >= self.width or bounds['right'] <= 0 or
                            bounds['top'] >= self.height or bounds['bottom'] <= 0):
                            log(f"⚠️ 元素不在屏幕可见范围内: {text}")
                            raise Exception("Element not visible on screen")
                    
                    # 尝试点击
                    try:
                        element.click()
                        log(f"✅ 成功点击: {text} (尝试 {attempt + 1})")
                        return True
                    except Exception as click_e:
                        log(f"❌ 点击失败 [{text}]: {str(click_e)}")
                        # 尝试通过坐标点击
                        if bounds:
                            center_x = (bounds['left'] + bounds['right']) // 2
                            center_y = (bounds['top'] + bounds['bottom']) // 2
                            self.d.click(center_x, center_y)
                            log(f"✅ 通过坐标点击成功: {text}")
                            return True
                        return False
                    
            except Exception as e:
                log(f"❌ 查找元素出错 [{text}]: {str(e)}")
            
            if attempt < max_swipes:
                log(f"未找到 '{text}'，向上滑动屏幕 (尝试 {attempt + 1}/{max_swipes})")
                self.smart_swipe("up", 
                               duration_min=swipe_duration, 
                               duration_max=swipe_duration + 0.2,
                               deviation_angle=10)
                time.sleep(wait_time)
        
        log(f"⚠️ 未找到元素 '{text}' (已尝试 {max_swipes} 次滑动)")
        return False

    def swipe_until(self, condition: Callable[[], bool], direction: str = "up",
                   max_swipes: int = 10, swipe_duration: float = 0.5, 
                   interval: float = 1.0) -> bool:
        """
        滑动直到满足条件或达到最大滑动次数
        
        Args:
            condition: 条件判断函数，返回True时停止滑动
            direction: 滑动方向
            max_swipes: 最大滑动次数
            swipe_duration: 滑动持续时间
            interval: 滑动间隔时间
            
        Returns:
            bool: 是否找到目标
        """
        for _ in range(max_swipes):
            if condition():
                return True
            self.smart_swipe(direction, duration_min=swipe_duration,
                            duration_max=swipe_duration + 0.1)
            time.sleep(interval)
        return False
    
    def smart_drag(
            self,
            d: u2.Device,
            origin: Union[Tuple[int, int], u2.xpath.XPathSelector, u2._selector.Selector],
            target: Union[Tuple[int, int], str] = "top",
            duration: float = 0.5
        ):
        # 获取起点坐标
        if isinstance(origin, tuple):
            from_x, from_y = origin
        elif hasattr(origin, 'center'):
            from_x, from_y = origin.center()  # ✅ 正确
        else:
            raise TypeError("origin 必须是坐标 (x, y) 或 uiautomator2 元素")

        # 获取目标坐标
        w, h = d.window_size()
        if isinstance(target, tuple):
            to_x, to_y = target
        elif isinstance(target, str):
            target = target.lower()
            to_x, to_y = {
                "top":    (from_x, 100),
                "bottom": (from_x, h - 100),
                "left":   (100, from_y),
                "right":  (w - 100, from_y),
                "center": (w // 2, h // 2),
            }.get(target, (from_x, from_y))
        else:
            raise TypeError("target 必须是坐标 (x, y) 或字符串方向（如 'top'）")

        d.drag(from_x, from_y, to_x, to_y, duration=duration)
        log(f"拖动：({from_x}, {from_y}) -> ({to_x}, {to_y})")


    def swipe_to_element(
            self,
            d: u2.Device,
            name,
            max_swipes: int = 6,
            swipe_duration: float = 0.5,
            interval: float = 1.0
        ) -> bool:
        """
        滑动直到找到指定元素
        
        Args:
            d: uiautomator2设备实例
            element: 目标元素
            direction: 滑动方向
            max_swipes: 最大滑动次数
            swipe_duration: 每次滑动的持续时间(秒)
            interval: 每次滑动后的等待时间(秒)
            
        Returns:
            bool: 是否成功找到元素
        """
        d.press("recent")  # 打开最近任务
        time.sleep(random.uniform(2, 3))
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            if d.xpath('//*[@resource-id="com.miui.home:id/clearAnimView"]').exists:
                log("✅ 进入最近任务界面")
                break
            else:
                d.press("recent")
                time.sleep(1)
                retry_count += 1
        else:
            log("❌ 未能进入最近任务界面，已达到最大重试次数")

        time.sleep(random.uniform(2, 3))

        for _ in range(max_swipes):
            nodes = d.xpath('//*[@resource-id="com.miui.home:id/title"]').all()
            for node in nodes:
                if node.text == name:
                    print("✅ 找到目标应用，点击它")
                    node.click()
                    return True

            # 如果没找到，向右滑动一次
            print("➡️ 向右滑动一页")
            window_size = d.window_size()
            start_x = int(window_size[0] * 0.2)  # 从左边开始
            end_x = int(window_size[0] * 0.8)    # 向右滑到右边
            y = int(window_size[1] * 0.5)
            d.swipe(start_x, y, end_x, y, duration=swipe_duration)
            time.sleep(interval)

        print("❌ 未找到目标应用")
        return False