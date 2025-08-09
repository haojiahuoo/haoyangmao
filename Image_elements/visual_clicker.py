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

    def find_and_click(self, retries=1, delay=2):
        """
        在 OCR 检测到的按钮中按 self.target_texts 的优先级选择并点击。
        成功返回 (cx, cy)，失败返回 False（保持原来的外部兼容性）。
        """
        for attempt in range(retries):
            print(f" 第{attempt + 1}次识别目标文本并尝试点击...")
            screen_path = self.screenshot(f'screen_click_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(
                screen_path,
                button_keywords=self.button_keywords
            )

            # best 保存当前找到的最佳候选： (priority_index, order_index, btn_dict)
            best = None
            order = 0
            for btn in elements.get('buttons', []):
                text = btn.get('text', '')
                # 按照 self.target_texts 的顺序判断优先级
                for prio_idx, target in enumerate(self.target_texts):
                    if target in text:
                        # 如果还没候选，或当前 target 优先级更高（索引更小），则替换
                        if best is None or prio_idx < best[0]:
                            best = (prio_idx, order, btn)
                        # 一旦当前 button 匹配到某个 target，就不必再检查后面的 target（避免重复）
                        break
                order += 1

            if best:
                btn = best[2]
                cx = int(btn['center'][0] * self.screen_width)
                cy = int(btn['center'][1] * self.screen_height)
                print(f"✅ 按优先级选择并点击匹配文本 '{btn.get('text')}'，点击坐标({cx}, {cy})")
                try:
                    self.d.click(cx, cy)
                except Exception as e:
                    print(f"⚠️ 调用 d.click 出错: {e}，尝试坐标点击备用方法")
                    self.d.click(cx, cy)  # 再试一次或你也可以做其他降级处理

                # 保存可视化结果（保持原行为）
                try:
                    self.ocr_helper.visualize_results(screen_path, f'screen_click_result_{attempt}.png')
                    print(f"📸 标注图已保存: screen_click_result_{attempt}.png")
                except Exception as e:
                    print(f"⚠️ 保存标注图失败: {e}")

                # 返回坐标（保持你之前的返回类型：非空值为 True）
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

    def match_text(self, retries=2, delay=2) -> str:
        for attempt in range(retries):
            screen_path = self.screenshot(f'screen_match_{attempt}.png')
            elements = self.ocr_helper.detect_clickable_elements(
                screen_path,
                button_keywords=self.button_keywords
            )

            matched_targets = []
            for btn in elements.get("buttons", []):
                text = btn["text"]
                for target in self.target_texts:
                    if target in text:
                        matched_targets.append(target)

            if matched_targets:
                # 按 target_texts 的顺序来选优先级最高的
                for target in self.target_texts:
                    if target in matched_targets:
                        print(f"✅ 匹配文本: {target}")
                        return target

            time.sleep(delay)
        return ""

    
    def __bool__(self):
        return self.exists()
