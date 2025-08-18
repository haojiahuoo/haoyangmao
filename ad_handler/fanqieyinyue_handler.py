import uiautomator2 as u2
import time
from utils.tools import *

class FanQieYinYueAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "任务完成",
            "开宝箱奖励已到账",
            "已成功领取",
            "今日签到可领",
            "再看一个",
            "领取成功",
            "说点什么",
            "开心收下",
            "领取奖励"
            
        ]
    
    def watch_ad(self, timeout: float = 300, check_interval: float = 3.0) -> bool:
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
                        if self.d(textContains="已领取"):
                            print("✅ 检测到--已领取, 任务完成")
                            self.d.press("back")  # 返回
                            print("✅ 返回主界面")
                            time.sleep(2) 
                        
                    if "领取成功" in elements[0].text:
                        if self.d.xpath('//*[contains(@text, "秒")]').exists:
                            print("✅ 检测到--秒, 任务完成")
                            click_by_xpath_text(self.d, xpaths='(//com.lynx.tasm.ui.image.UIImage)[2]')
                        else:    
                            print(f"✅ 任务完成-检测到: {elements[0].text}")
                            click_by_xpath_text(self.d, xpaths='//*[contains(@text, "领取成功")]/following-sibling::*[1]')
                    
                        
                    if "开心收下" in elements[0].text:
                        print(f"✅ 任务完成-检测到: {elements[0].text}")
                        click_by_xpath_text(self.d, "开心收下")
                
                if self.d.xpath('//*[@text="领取奖励"]').exists:  
                    click_by_xpath_text(self.d, "领取奖励")
                    
                if self.d.xpath('//*[@resource-id="app"]').exists:
                    self.d.press("back")
                    
                if self.d(textContains="金币收益").exists and time.time() - start_time > 30:
                    print("✅ 全部任务已完成，返回首页")
                    break
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 广告监控出错: {e}")
                continue
        
        print("⏰ 广告观看超时")
        return

