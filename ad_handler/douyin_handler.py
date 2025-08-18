import uiautomator2 as u2
import time, random
from typing import Optional
from Image_elements.visual_clicker import VisualClicker
from utils.tools import *
from utils.popuphandler import PopupHandler


class DouYinAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "领取成功", 
            "说点什么",
            "恭喜累计获得奖励",
            "后进入直播间"
        ]
    def watch_ad(self, timeout: float = 300, check_interval: float = 3.0) -> bool:
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
                    
                    if "恭喜累计获得奖励" in elements[0].text:
                        print("🗨️ 发现-累计获奖-弹窗")
                        click_by_xpath_text(self.d, "评价并收下金币")
                        
                    if "领取成功" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        elements[0].click()
                        time.sleep(random.uniform(1, 3))
                        if click_by_xpath_text(self.d, ["领取奖励", "评价并收下金币"]):
                            pass
                        else:
                            vc.set_targets(["评价并收下金币"])
                            vc.find_and_click()
                    
                    if "后进入直播间" in elements[0].text:
                        print("🗨️ 发现-进入直播间-弹窗")
                        click_by_xpath_text(self.d, "取消")
                                            
                    if "说点什么" in elements[0].text:
                        print("🗨️ 发现-直播-弹窗")
                        while_start_time = time.time()
                        task_completed = False
                        while True:
                            # 先检查是否已完成任务
                            if self.d(textContains="已领取"):
                                print("✅ 检测到--已领取, 任务完成")
                                task_completed = True
                                break
                            # 再检查是否超时
                            if time.time() - while_start_time >= 35:
                                print("⏰ 超时35秒未检测到'已领取'")
                                task_completed = True
                                break  
                            if self.d(textContains="添加到主屏幕").exists:
                                ph.check_and_handle_popup()
                            time.sleep(1)  # 避免频繁检查
                        # 任务完成或超时后的处理
                        if task_completed:
                            self.d.press("back")  # 返回
                            time.sleep(2)


                if self.d.xpath('//*[@resource-id="app"]').exists:
                        self.d.press("back")
                        
                if self.d(textContains="领奖提醒").exists and time.time() - start_time > 30:
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

