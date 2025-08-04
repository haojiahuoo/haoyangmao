import uiautomator2 as u2
import time
from typing import Optional
from Image_elements.visual_clicker import VisualClicker
from utils.device import d

class DouYinAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "任务完成",
            "开宝箱奖励已到账",
            "已成功领取",
            "今日签到可领",
            "再看一个",
            "领取成功", #11 
            "说点什么",
            "恭喜累计获得奖励",
        ]
        self.claim_texts = [
            "恭喜累计获得奖励",
            "再看一个"
            
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
                    
                    if "恭喜累计获得奖励" in elements[0].text:
                        print("🗨️ 发现-累计获奖-弹窗")
                        element = self.d(textContains="评价并收下金币")
                        element.click()
                        print("✅ 点击--收下金币")
                        time.sleep(1)
                        continue  # 继续监控广告
                        
                    if "领取成功" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        elements[0].click()
                        time.sleep(2)
                        if d.xpath('//*[@resource-id="app"]').exists:
                            self.d.press("back")
                        # 尝试领取奖励
                        claim_xpath = " | ".join(
                            f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                        )
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                print(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "再看一个" in claims[0].text:
                                print("🗨️ 发现-再看一个-弹窗")
                                claim = self.d(textContains="领取奖励")
                                claim.click()
                                print("✅ 点击--领取奖励")
                                time.sleep(1)
                                continue  # 继续监控广告        
                            
                if self.d(textContains="领奖提醒").exists and time.time() - start_time > 30:
                    print("✅ 任务完成已返回任务页")
                    break
                
                # 检查是否需要返回首页
                vc = VisualClicker(d, target_texts=["金币收益"])
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

