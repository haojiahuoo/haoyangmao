import uiautomator2 as u2
import time
from typing import Optional
from Image_elements.visual_clicker import VisualClicker
from utils.tools import *
from utils.popuphandler import PopupHandler


class WuKongAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "继续播放视频内容",
            "关闭",
            "领取成功",
            "再看一条",
            "开心收下",
            "跳过",
            "秒小游戏",
            "后进入直播间",
           " 看视频再"
        ]
     
    def watch_ad(self, timeout: float = 500, check_interval: float = 3.0) -> bool:
        vc = VisualClicker(self.d)
        ph = PopupHandler(self.d)
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
                
                    if any(t in elements[0].text for t in ["继续播放视频内容", "再看一条", "开心收下", "看视频再"]):
                        click_by_xpath_text(self.d, elements[0].text)
                        
                    if "说点什么" in elements[0].text:
                        print("🗨️ 发现-直播-弹窗")
                        self.d.press("back")  # 返回
                        time.sleep(2)
                        click_by_xpath_text(self.d, "关闭")
                        
                        
                    if "领取成功" in elements[0].text:
                        print("✅ 广告观看完成")
                        if self.d.xpath('//*[@text="跳过"]').exists:
                            click_by_xpath_text(self.d, "跳过")
                            time.sleep(2)
                        else:    
                            self.d.press("back")
                    
                    if "秒小游戏" in elements[0].text:
                        if click_by_xpath_text('//*[@text="提前拿奖励"]/../../preceding-sibling::*[@class="android.widget.FrameLayout"][1]'):
                            click_by_xpath_text(self.d, "立即退出")
                    
                    if "关闭" in elements[0].text:
                        if self.d(textContains="s").wait_gone(timeout=45):
                            self.d.press("back")  # 返回
                            time.sleep(2)
                            click_by_xpath_text(self.d, "看视频再")
                        if self.d.xpath('//*[@resource-id="app"]').exists:
                                self.d.press("back")
                    
                if self.d.xpath('//*[@resource-id="app"]').exists:
                        self.d.press("back")
                            
                if self.d(textContains="去提现").exists and time.time() - start_time > 30:
                    print("✅ 任务完成已返回任务页")
                    break
                elif self.d.xpath('//*[contains(@text, "明天再来")]').exists:
                    print("✅ 打卡任务已完成")
                    self.d.press("back")  # 返回
                    break
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 广告监控出错: {e}")
                continue
        
        print("⏰ 广告观看超时")
        return

