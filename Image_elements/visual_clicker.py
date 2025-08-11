import time
import uiautomator2 as u2
from typing import List, Optional
from Image_elements.ocr_helper import SmartController  # 替换为你实际的 OCR 控制器路径

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

    def find_and_click(self, target=None, retries=1, delay=2):
        """
        点击 OCR 检测到的按钮。
        target:
            None  → 按 set_targets 优先级选择
            int   → 按索引选择（0 为第一个）
            str   → 按文本模糊匹配
        成功返回 (cx, cy)，失败返回 False。
        """
        for attempt in range(retries):
            print(f" 第{attempt + 1}次识别目标文本并尝试点击...")
            screen_path = self.screenshot(f'screen_click_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(
                screen_path,
                button_keywords=self.button_keywords
            )

            buttons = elements.get('buttons', [])
            if not buttons:
                print("❌ 未检测到任何可点击元素")
                time.sleep(delay)
                continue

            chosen_btn = None

            # 1️⃣ 如果是 int 索引
            if isinstance(target, int):
                if 0 <= target < len(buttons):
                    chosen_btn = buttons[target]
                else:
                    print(f"⚠️ 索引 {target} 超出范围（共 {len(buttons)} 个按钮）")

            # 2️⃣ 如果是 str 文字匹配
            elif isinstance(target, str):
                for btn in buttons:
                    if target in btn.get('text', ''):
                        chosen_btn = btn
                        break
                if not chosen_btn:
                    print(f"⚠️ 未找到包含文本 '{target}' 的按钮")

            # 3️⃣ 如果是 None，走 set_targets 优先级逻辑
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

            # ✅ 执行点击
            if chosen_btn:
                cx = int(chosen_btn['center'][0] * self.screen_width)
                cy = int(chosen_btn['center'][1] * self.screen_height)
                print(f"✅ 点击 '{chosen_btn.get('text')}'，坐标 ({cx}, {cy})")

                try:
                    self.d.click(cx, cy)
                except Exception as e:
                    print(f"⚠️ d.click 出错: {e}，尝试降级点击")
                    self.d.click(cx, cy)

                # 保存标注图
                try:
                    self.ocr_helper.visualize_results(screen_path, f'screen_click_result_{attempt}.png')
                    print(f"📸 标注图已保存: screen_click_result_{attempt}.png")
                except Exception as e:
                    print(f"⚠️ 保存标注图失败: {e}")

                return (cx, cy)

            time.sleep(delay)

        print("❌ 未找到目标文本，点击失败")
        return False


    def exists(self, retries=2, delay=2) -> bool:
        for attempt in range(retries):
            print(f"🔍 第{attempt + 1}次检测目标文本是否存在...")
            screen_path = self.screenshot(f'screen_check_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(
                screen_path,
                button_keywords=self.button_keywords
            )

            for btn in elements.get('buttons', []):
                text = btn['text']
                if any(target in text for target in self.target_texts):
                    print(f"✅ 检测到目标文本 '{text}'")
                    return True
            time.sleep(delay)
        print("❌ 未检测到目标文本")
        return False

    def match_text(self, retries=2, delay=2, return_full_text=False) -> str:
        for attempt in range(retries):
            screen_path = self.screenshot(f'screen_match_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(
                screen_path,
                button_keywords=self.button_keywords
            )

            # 提取所有按钮文本，方便按优先级匹配
            buttons_text_map = [(btn["text"], btn) for btn in elements.get("buttons", [])]

            # 按 target_texts 顺序优先匹配
            for target in self.target_texts:
                for full_text, _ in buttons_text_map:
                    if target in full_text:
                        if return_full_text:
                            print(f"✅ 匹配完整文本: {full_text}")
                            return full_text
                        else:
                            print(f"✅ 匹配关键词: {target}")
                            return target

            time.sleep(delay)
        return ""



    
    def __bool__(self):
        return self.exists()
