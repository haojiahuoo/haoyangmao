import uiautomator2 as u2
import time,random
from typing import Optional
from utils.tools import *
from utils.smart_swipe import SmartSwipe

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
            "聊一聊",
            "领取额外金币"
        ]
        self.claim_texts = [
            "明日签到可领",
            "再看1个广告再得",
            "恭喜完成观看任务" 
        ]

    def watch_ad(self, timeout: float = 1000, check_interval: float = 3.0) -> bool:
        ss = SmartSwipe(self.d)
        time.sleep(10)  # 等待界面稳定
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
                        
                    if "说点什么" in elements[0].text or "聊一聊" in elements[0].text:
                        log("🗨️ 发现-直播-弹窗")
                        while_start_time = time.time()
                        task_completed = False
                        
                        while True:
                            # 先检查是否已完成任务
                            if self.d(textContains="已领取"):
                                log("✅ 检测到--已领取, 任务完成")
                                task_completed = True
                                break
                            # 再检查是否超时
                            if time.time() - while_start_time >= random.uniform(40, 50):
                                log("⏰ 超时35秒未检测到'已领取'")
                                task_completed = True
                                break  
                            if self.d(textContains="添加到主屏幕").exists:
                                click_by_xpath_text(self.d, "取消")
                            
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
                                    log(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                                
                                if "再看1个广告再得" in claims[0].text:
                                    log("🗨️ 发现-再看1个广告-弹窗")
                                    click_by_xpath_text(self.d, "领取奖励")
                                    

                            if click_by_xpath_text(self.d, "退出"):  # 退出直播间
                                log("✅ 返回主界面")
                                time.sleep(2)
                            
                    if "已成功领取" in elements[0].text:
                        log(f"✅ 任务完成（检测到: {elements[0].text}）")
                        self.d.press("back")  # 返回
                        time.sleep(2)
                        # 尝试领取奖励
                        claim_xpath = " | ".join(
                            f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                        )
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                log(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "再看1个广告再得" in claims[0].text:
                                log("🗨️ 发现-再看1个广告-弹窗")
                                click_by_xpath_text(self.d, "领取奖励")
                            
                    if "开宝箱奖励已到账" in elements[0].text:
                        log("🗨️ 发现-开宝箱奖励-弹窗")
                        element = self.d.xpath('//*[contains(@text, "开宝箱奖励已到账")]/following-sibling::*[contains(@text, "去看广告得")]')
                        element.click()
                        log("✅ 点击--去看广告得金币")
                        time.sleep(1)
                        
                        claim_xpath = " | ".join(
                            f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                        )
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                log(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "再看1个广告再得" in claims[0].text:
                                log("🗨️ 发现-再看1个广告-弹窗")
                                click_by_xpath_text(self.d, "领取奖励")
                        
                    if "再看一个" in elements[0].text:
                        log("🗨️ 发现-再看一个-弹窗")
                        element = self.d.xpath('//*[contains(@text, "再看一个")]/following-sibling::*[contains(@text, "领取奖励")]')
                        element.click()
                        log("✅ 点击--再看一个")
                        time.sleep(3)
                        continue  # 继续监控广告
                    
                    if "领取额外金币" in elements[0].text:
                        log("🗨️ 发现-领取额外金币-弹窗")
                        click_by_xpath_text(self.d, "领取额外金币")
                        time.sleep(random.uniform(1, 3))
                        ss.swipe_to_element(self.d, "快手极速版")
                        
                if self.d(text="安装新版本").exists:
                    time.sleep(random.uniform(1, 3))
                    click_by_xpath_text(self.d, "取消") 
                    
                if self.d(text="欢迎使用支付宝").exists:
                    time.sleep(random.uniform(1, 3))
                    self.d.press("back")  # 返回
                if self.d(text="请验证指纹").exists:
                    time.sleep(random.uniform(1, 3))
                    ss.swipe_to_element(self.d, "快手极速版")
                    
                if self.d(text="去完成任务").exists:
                    time.sleep(random.uniform(1, 3))
                    click_by_xpath_text(self.d, "去完成任务")
                    
                if self.d(text="荣耀安全提示").exists:
                    time.sleep(random.uniform(1, 3))
                    click_by_xpath_text(self.d, "允许")
                    
                if self.d(textContains="猜你喜欢").exists and time.time() - start_time > 30:
                    log("✅ 全部任务已完成，返回首页")
                    return
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                log(f"❌ 广告监控出错: {e}")
                continue
        
        log("⏰ 广告观看超时")
        if self.d(textContains="猜你喜欢").exists:
            self.d.press("back")
            return

