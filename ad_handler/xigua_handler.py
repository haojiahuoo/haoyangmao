import uiautomator2 as u2
import time, random
from typing import Optional
from Image_elements.visual_clicker import VisualClicker
from utils.device import d
from utils.tools import *

class XiGuaAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "领取成功", 
            "说点什么",
        ]
     
    def watch_ad(self, timeout: float = 300, check_interval: float = 3.0) -> bool:
        vc = VisualClicker(d)
        time.sleep(10)  # 等待界面稳定
        print("[开启刷广告模式.....]")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 检查完成状态
                completion_xpath = " | ".join(
                    f'//*[contains(@text, "{title}")]' for title in self.completion_titles
                )
                if elements := self.d.xpath(completion_xpath).all():
                    for i, element in enumerate(elements, 1):
                        print(f"匹配元素1 {i}/{len(elements)}: {element.text}")
                    
                    if "领取成功" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        elements[0].click()
                        vc.target_texts = ["评价并关闭"]
                        vc.find_and_click()
                    
                if d.xpath('//*[@resource-id="app"]').exists:
                        self.d.press("back")  
                            
                # 检查是否需要返回首页
                vc.target_texts = ["金币收益"]
                matched_text = vc.match_text()
                if matched_text == "金币收益":
                    print("✅ 全部任务已完成，返回首页")
                    break
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 广告监控出错: {e}")
                continue
        
        print("⏰ 广告观看超时")
        return

