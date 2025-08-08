import time
import uiautomator2 as u2
from typing import List
from Image_elements.ocr_helper import SmartController  # 替换为你实际的 OCR 控制器路径

class VisualClicker:
    def __init__(self, device: u2.Device, target_texts: List[str] = None):
        self.d = device
        self.ocr_helper = SmartController()
        self.target_texts = target_texts or []
        self.screen_width, self.screen_height = self.d.window_size()

    def screenshot(self, path='screen.png'):
        self.d.screenshot(path)
        return path

    def find_and_click(self, retries=1, delay=2) -> bool:
        for attempt in range(retries):
            print(f" 第{attempt + 1}次识别目标文本并尝试点击...")
            screen_path = self.screenshot(f'screen_click_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(screen_path)

            for btn in elements.get('buttons', []):
                text = btn['text']
                if any(target in text for target in self.target_texts):
                    cx = int(btn['center'][0] * self.screen_width)
                    cy = int(btn['center'][1] * self.screen_height)
                    print(f"✅ 找到匹配文本 '{text}'，点击坐标({cx}, {cy})")
                    self.d.click(cx, cy)
                    self.ocr_helper.visualize_results(screen_path, f'screen_click_result_{attempt}.png')
                    print(f"📸 标注图已保存: screen_click_result_{attempt}.png")
                    return True
            time.sleep(delay)
        print("❌ 未找到目标文本，点击失败")
        return False

    def exists(self, retries=2, delay=2) -> bool:
        for attempt in range(retries):
            print(f"🔍 第{attempt + 1}次检测目标文本是否存在...")
            screen_path = self.screenshot(f'screen_check_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(screen_path)

            for btn in elements.get('buttons', []):
                text = btn['text']
                if any(target in text for target in self.target_texts):
                    print(f"✅ 检测到目标文本 '{text}'")
                    return True
            time.sleep(delay)
        print("❌ 未检测到目标文本")
        return False

    def match_text(self, retries=2, delay=2) -> str:
        """
        检测目标文本，返回匹配到的第一个目标文本，未匹配返回空字符串
        """
        for attempt in range(retries):
            screen_path = self.screenshot(f'screen_match_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(screen_path)

            for btn in elements.get("buttons", []):
                text = btn["text"]
                for target in self.target_texts:
                    if target in text:
                        print(f"✅ 匹配文本: {target}")
                        return target
            time.sleep(delay)
        return ""
    
    def find_text_position(self, target_text: str, retries=2, delay=2):
        """
        查找指定文本的中心坐标（用于拖动或其他操作）
        :param target_text: 要查找的文本
        :return: (x, y) 坐标元组 或 None
        """
        for attempt in range(retries):
            screen_path = self.screenshot(f'screen_pos_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(screen_path)

            for btn in elements.get("buttons", []):
                text = btn["text"]
                if target_text in text:
                    cx = int(btn["center"][0] * self.screen_width)
                    cy = int(btn["center"][1] * self.screen_height)
                    print(f"🎯 文本 '{target_text}' 坐标: ({cx}, {cy})")
                    return cx, cy
            time.sleep(delay)
        print(f"❌ 未找到文本 '{target_text}' 的坐标")
        return None

    def __bool__(self):
        return self.exists()

