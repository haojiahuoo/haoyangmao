import time, random
import uiautomator2 as u2
from typing import List, Optional
from Image_elements.ocr_helper import SmartController  # 替换为你实际的 OCR 控制器路径
from logger import log  # 替换为你实际的日志记录器路径
class VisualClicker:
    def __init__(self, device: u2.Device, target_texts: List[str] = None, button_keywords: Optional[List[str]] = None):
        self.d = device
        self.ocr_helper = SmartController()
        self.target_texts = target_texts or []
        self.button_keywords = button_keywords
        self.screen_width, self.screen_height = self.d.window_size()

    def set_targets(self, texts: List[str]):
        """
        一键设置同时更新 target_texts 和 button_keywords，
        确保OCR识别和点击筛选用同一套关键词
        """
        self.target_texts = texts
        self.button_keywords = texts

    def screenshot(self, path='screen.png'):
        self.d.screenshot(path)
        return path

    def find_and_click(self, target=None, retries=1, delay=2, elements=None):
        for attempt in range(retries):
            log(f" 第{attempt + 1}次识别目标文本并尝试点击...")

            # 优先用 match_text 的缓存结果
            if elements is None and hasattr(self, "_last_elements") and self._last_elements:
                elements = self._last_elements
                log("📌 使用 match_text() 的缓存结果")
                screen_path = None
            elif elements is None:
                screen_path = self.screenshot(f'screen_click_{attempt}.png')
                elements = self.ocr_helper.detect_clickable_elements(
                    screen_path,
                    button_keywords=self.button_keywords
                )
            else:
                screen_path = None

            buttons = elements.get('buttons', [])
            if not buttons:
                log("❌ 未检测到任何可点击元素")
                time.sleep(delay)
                continue

            chosen_btn = None
            if isinstance(target, int):
                if 0 <= target < len(buttons):
                    chosen_btn = buttons[target]
            elif isinstance(target, str):
                for btn in buttons:
                    if target in btn.get('text', ''):
                        chosen_btn = btn
                        break
            else:
                best = None
                order = 0
                for btn in buttons:
                    text = btn.get('text', '')
                    for prio_idx, t in enumerate(self.target_texts):
                        if t in text:
                            if best is None or prio_idx < best[0]:
                                best = (prio_idx, order, btn)
                            break
                    order += 1
                if best:
                    chosen_btn = best[2]

            if chosen_btn:
                cx = int(chosen_btn['center'][0] * self.screen_width)
                cy = int(chosen_btn['center'][1] * self.screen_height)
                log(f"✅ 点击 '{chosen_btn.get('text')}'，坐标 ({cx}, {cy})")
                self.d.click(cx, cy)
                if screen_path:
                    self.ocr_helper.visualize_results(screen_path, f'screen_click_result_{attempt}.png')
                return (cx, cy)

            time.sleep(delay)

        log("❌ 未找到目标文本，点击失败")
        return False

    def exists(self, retries=2, delay=2) -> bool:
        for attempt in range(retries):
            log(f"🔍 第{attempt + 1}次检测目标文本是否存在...")
            screen_path = self.screenshot(f'screen_check_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(
                screen_path,
                button_keywords=self.button_keywords
            )

            for btn in elements.get('buttons', []):
                text = btn['text']
                if any(target in text for target in self.target_texts):
                    log(f"✅ 检测到目标文本 '{text}'")
                    return True
            time.sleep(delay)
        log("❌ 未检测到目标文本")
        return False

    def match_text(self, retries=2, delay=2, return_full_text=False):
        self._last_elements = None  # 清空上一次结果
        for attempt in range(retries):
            screen_path = self.screenshot(f'screen_match_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(
                screen_path,
                button_keywords=self.button_keywords
            )
            self._last_elements = elements  # 存下来给 find_and_click 用

            matched_targets = []
            for target in self.target_texts:   # 先按你的目标顺序
                for btn in elements.get("buttons", []):
                    text = btn["text"]
                    if target in text:
                        matched_targets.append((target, text))
                        break
                    
            if matched_targets:
                for target, full_text in matched_targets:
                    if target in self.target_texts:
                        if return_full_text:
                            log(f"✅ 匹配完整文本: {full_text}")
                            return full_text
                        else:
                            log(f"✅ 匹配关键词: {target}")
                            return target
            time.sleep(delay)
        return ""
    
    def click_by(self, text) -> bool:
        self.set_targets([f"{text}"])
        matched_text = self.match_text()
        if matched_text == text:
            log(f"🗨️ 发现-{text}-元素")
            self.find_and_click()
            log(f"🗨️ 点击-{text}-元素")
            time.sleep(random.uniform(1, 3))
            return True
        else:
            log(f"❌ 未找到目标文本: {text}")
            return False
    
    def __bool__(self):
        return self.exists()
