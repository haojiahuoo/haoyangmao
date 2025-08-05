import uiautomator2 as u2
import time
from typing import Optional
from Image_elements.visual_clicker import VisualClicker
from utils.device import d
from utils.tools import *
class WuKongAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
        
        ]
        self.claim_texts = [
            "恭喜您已获得"
        ]

    def watch_ad(self, timeout: float = 300, check_interval: float = 3.0) -> bool:
        vc = VisualClicker(d)
        time.sleep(10)  # 等待界面稳定
        
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
                        
                    if d.xpath("//*[contains(@text, '关闭')]").wait_gone(timeout=45):
                        d.press("back")
                        click_by_xpath_text(d, "关闭")
                        # 尝试领取奖励
                        claim_xpath = " | ".join(
                            f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                        )
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                print(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "恭喜您已获得" in claims[0].text:
                                print("🗨️ 发现-恭喜获得-弹窗")
                                click_by_xpath_text(d, "看视频再得")
                                print("✅ 点击--看视频再得")
                                time.sleep(1)
                                continue  # 继续监控广告    
                            
                            
                        if "说点什么" in elements[0].text:
                            print("🗨️ 发现-直播-弹窗") 
                            time.sleep(5) 
                            d.press("back")   
                            click_by_xpath_text(d, "坚决退出")
                            click_by_xpath_text(d, "关闭")
                if self.d(textContains="领奖提醒").exists and time.time() - start_time > 30:
                    print("✅ 任务完成已返回任务页")
                    break
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 广告监控出错: {e}")
                continue
        
        print("⏰ 广告观看超时")
        return

