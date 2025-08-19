import uiautomator2 as u2
import time, random
from typing import Optional
from utils.tools import *


class HongGuoAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "领取成功",
            "说点什么", # 1
            
        ]

    def watch_ad(self, timeout: float = 300, check_interval: float = 3.0) -> bool:
        time.sleep(5)  # 等待界面稳定
        log("[开启刷广告模式.....]")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 检查完成状态
                completion_xpath = " | ".join(
                    f'//*[contains(@text, "{title}")]' for title in self.completion_titles
                )
                if elements := self.d.xpath(completion_xpath).all():
                    for i, element in enumerate(elements, 1):
                        log(f"匹配元素1 {i}/{len(elements)}: {element.text}")
                
                    if "说点什么" in elements[0].text:
                        log("🗨️ 发现-直播-弹窗")
                        time.sleep(2)
                        self.d.press("back")
                        click_by_xpath_text(self.d, "退出")
                        
                    if "领取成功" in elements[0].text:
                        log(f"✅ 任务完成（检测到: {elements[0].text}）")
                        self.d.press("back")

                if self.d.xpath('//*[@resource-id="app"]').exists:
                    self.d.press("back")
                    
                
                if  self.d(textContains="开心收下").exists:
                    log("✅ 检测到: 开心收下")
                    time.sleep(random.uniform(1, 3))
                    click_by_xpath_text(self.d, "开心收下")
                    
                if  self.d(textContains="后进入直播间").exists:
                    log("✅ 检测到: 开心收下")
                    time.sleep(random.uniform(1, 3))
                    click_by_xpath_text(self.d, "取消")
                    
                if self.d(textContains="领取奖励").exists:
                    log("✅ 任务完成（检测到: 领取奖励）")
                    time.sleep(random.uniform(1, 3))
                    click_by_xpath_text(self.d, "领取奖励")
                    
                if self.d(textContains="明日一键领金币").exists:
                    log("✅ 任务完成（检测到: 明日一键领金币）")
                    time.sleep(random.uniform(1, 3))
                    break
                
                if self.d(textContains="金币收益").exists and time.time() - start_time > 30:
                    log("✅ 看完广告返回首页")
                    break
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                log(f"❌ 广告监控出错: {e}")
                continue
        
        log("⏰ 广告观看超时")
        return

