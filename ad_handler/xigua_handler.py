import uiautomator2 as u2
import time, random
from typing import Optional
from Image_elements.visual_clicker import VisualClicker
from utils.tools import *

class XiGuaAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "领取成功", 
            "说点什么",
            "看广告已累计"
        ]
     
    def watch_ad(self, timeout: float = 300, check_interval: float = 3.0) -> bool:
        vc = VisualClicker(self.d)
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
                    
                    if "看广告已累计" in elements[0].text:
                        print("🗨️ 发现-累计获奖-弹窗")
                        click_by_xpath_text(self.d, "评价并关闭")
                    
                        
                    if "领取成功" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        elements[0].click()
                        time.sleep(random.uniform(1, 3))
                        if click_by_xpath_text(self.d, ["领取奖励", "评价并关闭"], wait_gone=False):
                            pass
                        else:
                            vc.set_targets(["评价并关闭"])
                            vc.find_and_click()

                if self.d.xpath('//*[@text="邀请你参与西瓜体验反馈"]').exists:
                    self.d.press("back")
                
                if self.d.xpath('//*[@resource-id="app"]').exists:
                    self.d.press("back")  
                
                if self.d(textContains="领奖提醒").exists:
                    print("✅ 任务完成已返回任务页")
                    break  
                if self.d(textContains="今日一键领取金币").exists:
                    print("✅ 任务完成已返回任务页")
                    break            
                 # 检查是否需要返回首页
                vc.set_targets(["日常任务", "金币收益"])
                matched_text = vc.match_text()
                if matched_text in ("日常任务", "金币收益") and time.time() - start_time > 30:
                    print("✅ 全部任务已完成，返回首页")
                    break
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 广告监控出错: {e}")
                continue
        
        print("⏰ 广告观看超时")
        return

