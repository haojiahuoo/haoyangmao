import uiautomator2 as u2
import time,random
from typing import Optional
from utils.tools import *
from utils.popuphandler import PopupHandler

class KuaiShouAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "任务完成",
            "开宝箱奖励已到账",
            "已成功领取",
            "今日签到可领",
            "再看一个",  # 1
            "领取成功",
            "说点什么", # 1
        ]
        self.claim_texts = [
            "明日签到可领",
            "再看1个广告再得",
            "恭喜完成观看任务" 
        ]

    def watch_ad(self, timeout: float = 300, check_interval: float = 3.0) -> bool:
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
                            
                            claim_xpath = " | ".join(
                                f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                            )
                            if claims := self.d.xpath(claim_xpath).all():
                                for i, claim in enumerate(claims, 1):
                                    print(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                                
                                if "再看1个广告再得" in claims[0].text:
                                    print("🗨️ 发现-再看1个广告-弹窗")
                                    click_by_xpath_text(self.d, "领取奖励")
                                    

                            if click_by_xpath_text(self.d, "退出"):  # 退出直播间
                                print("✅ 返回主界面")
                                time.sleep(2)
                            
                    if "已成功领取" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        self.d.press("back")  # 返回
                        time.sleep(2)
                        # 尝试领取奖励
                        claim_xpath = " | ".join(
                            f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                        )
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                print(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "再看1个广告再得" in claims[0].text:
                                print("🗨️ 发现-再看1个广告-弹窗")
                                click_by_xpath_text(self.d, "领取奖励")
                            
                    if "开宝箱奖励已到账" in elements[0].text:
                        print("🗨️ 发现-开宝箱奖励-弹窗")
                        element = self.d.xpath('//*[contains(@text, "开宝箱奖励已到账")]/following-sibling::*[contains(@text, "去看广告得")]')
                        element.click()
                        print("✅ 点击--去看广告得金币")
                        time.sleep(1)
                        
                        claim_xpath = " | ".join(
                            f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                        )
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                print(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "再看1个广告再得" in claims[0].text:
                                print("🗨️ 发现-再看1个广告-弹窗")
                                click_by_xpath_text(self.d, "领取奖励")
                        
                    if "再看一个" in elements[0].text:
                        print("🗨️ 发现-再看一个-弹窗")
                        element = self.d.xpath('//*[contains(@text, "再看一个")]/following-sibling::*[contains(@text, "领取奖励")]')
                        element.click()
                        print("✅ 点击--再看一个")
                        time.sleep(3)
                        continue  # 继续监控广告
                    
                if self.d(textContains="猜你喜欢").exists and time.time() - start_time > 30:
                    print("✅ 全部任务已完成，返回首页")
                    return
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 广告监控出错: {e}")
                continue
        
        print("⏰ 广告观看超时")
        if self.d(textContains="猜你喜欢").exists:
            self.d.press("back")
            return

