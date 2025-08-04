import uiautomator2 as u2
import time
from typing import Optional

class JinRiTouTiaoAdWatcher:
    def __init__(self, d: u2.Device):
    
        self.d = d
        self.completion_titles = [
            "再看一个",  # 1
            "领取成功",
            "说点什么", # 1
            "逛街最多再领"
        ]
        self.claim_texts = [
            "恭喜已获得"
            
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
                        time.sleep(2)
                        self.d.xpath("//*[@resource-id='com.ss.android.article.lite:id/a9k']").click()
                        
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                print(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "恭喜已获得" in claims[0].text:
                                print("🗨️ 发现-恭喜已获得-弹窗")
                                claim = self.d(textContains="看视频")
                                claim.click()
                                print("✅ 点击--看视频")
                                time.sleep(1)
                                continue  # 继续监控广告   
                            
                    if "领取成功" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        elements[0].click()
                        time.sleep(2)
                        # 尝试领取奖励
                        claim_xpath = " | ".join(
                            f'//*[contains(@text, "{text}")]' for text in self.claim_texts
                        )
                        if claims := self.d.xpath(claim_xpath).all():
                            for i, claim in enumerate(claims, 1):
                                print(f"匹配元素2 {i}/{len(claims)}: {claim.text}")
                            
                            if "恭喜已获得" in claims[0].text:
                                print("🗨️ 发现-恭喜已获得-弹窗")
                                claim = self.d(textContains="看视频")
                                claim.click()
                                print("✅ 点击--看视频")
                                time.sleep(1)
                                continue  # 继续监控广告
                    
                    if "逛街最多再领" in elements[0].text:
                        print(f"✅ 任务完成（检测到: {elements[0].text}）")
                        elements[0].click()
                        time.sleep(2)
                        break
                    
                if self.d(textContains="寻宝得现金").exists:
                    print("✅ 看完广告返回游戏")
                    break
                elif self.d(textContains="现金收益").exists:
                    print("✅ 看完广告返回首页")
                    break
                else:
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 广告监控出错: {e}")
                continue
        
        print("⏰ 广告观看超时")
        return

