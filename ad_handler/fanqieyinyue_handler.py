import uiautomator2 as u2
import time

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
        ]
        self.claim_texts = [
            "明日签到可领",
            "再看一个",
            "恭喜完成观看任务",
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
                        print(f"✅ 任务完成-检测到: {elements[0].text}")
                        self.d.xpath('//*[contains(@text, "领取成功")]/following-sibling::*[2]').click()
                        time.sleep(2)
                        # 尝试领取奖励
                        claim_xpath = " | ".join(
                            f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                        )
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                print(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "再看一个" in claims[0].text:
                                print("🗨️ 发现-再看一个-弹窗")
                                claim = self.d(textContains="再看一个")
                                claim.click()
                                print("✅ 点击--再看一个")
                                time.sleep(1)
                                continue  # 继续监控广告
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

