import uiautomator2 as u2
import time, random
from typing import Optional
from utils.tools import *


class JinRiTouTiaoAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "领取成功",
            "说点什么", # 1
            "逛街最多再领"
        ]

    def watch_ad(self, timeout: float = 500, check_interval: float = 3.0) -> bool:
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
                
                    if "说点什么" in elements[0].text:
                        print("🗨️ 发现-直播-弹窗")
                        time.sleep(2)
                        self.d.xpath("//*[@resource-id='com.ss.android.article.lite:id/a9k']").click()
                        click_by_xpath_text(self.d, "退出直播")
                        
                    if "领取成功" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        elements[0].click()
                        time.sleep(random.uniform(1, 3))
                        click_by_xpath_text(self.d, "看视频")
                    
                    if "逛街最多再领" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        elements[0].click()
                        time.sleep(2)
                        break

                if self.d.xpath('//*[@resource-id="app"]').exists:
                    self.d.press("back")
                    continue

                if self.d(textContains="寻宝得现金").exists:
                    print("✅ 看完广告返回游戏")
                    break
                elif self.d(textContains="现金收益").exists and time.time() - start_time > 30:
                    print("✅ 看完广告返回首页")
                    break
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 广告监控出错: {e}")
                continue
        
        print("⏰ 广告观看超时")
        return

