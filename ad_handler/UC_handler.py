import uiautomator2 as u2
import time, random
from utils.tools import *
from logger import bind_logger
from Image_elements.visual_clicker import VisualClicker
from utils.popuphandler import PopupHandler

class UCAdWatcher:
    def __init__(self, device: Union[str, u2.Device]):
        """初始化UC广告监控器"""
        if isinstance(device, str):
            self.d = u2.connect(device)
            self.device_id = device
        else:
            self.d = device
            self.device_id = getattr(device, "serial", str(device))
        
        # 绑定日志器
        self.log, self.log_error, self.log_debug = bind_logger(self.device_id)
        
        # 广告完成标题列表
        self.completion_titles = [
            "奖励已领取",
            "说点什么",
            "进入微信",
            "完成App下载",
            "恭喜获得奖励",
            "完成App安装",
            "去体验15秒可立即领奖",
            "奖励已发放",
            "摇动手机",
            "奖励将于"
            
        ]

    def watch_ad(self, timeout: float = 1000, check_interval: float = 3.0) -> bool:
        self.log(f"开始监控广告，超时时间: {timeout}秒")
        vc = VisualClicker(self.d)
        ph = PopupHandler(self.d)
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                completion_xpath = " | ".join(
                    f'//*[contains(@text, "{title}")]' for title in self.completion_titles
                )
                elements = self.d.xpath(completion_xpath).all()
                if elements:
                    for i, element in enumerate(elements, 1):
                        self.log_debug(f"匹配元素1 {i}/{len(elements)}: {element.text}")

                    if element and any(t in elements[0].text for t in ["奖励已发放", "摇动手机", "奖励将于"]):
                        if elements[0].text == "奖励已发放":
                            self.log("✅ 发现奖励已发放")
                            click_by_xpath_text(self.d, "奖励已发放")
                        elif elements[0].text == "摇动手机":
                            self.log("✅ 发现摇动手机弹框")
                            if self.d(textContains="反馈").exists:
                                self.log("🗨️ 发现反馈弹窗")
                                click_by_xpath_text(self.d, xpaths="//*[contains(@text, '反馈')]/following-sibling::*[1]")  
                        elif elements[0].text == "奖励将于":
                            self.log("✅ 发现奖励将于弹框")
                            if click_by_xpath_text(self.d, "奖励将于", wait_gone=True, timeout=45):
                                self.log("✅ 奖励将于弹框已消失")
                                time.sleep(random.uniform(2, 3))
                                click_by_xpath_text(self.d, xpaths="//*[contains(@text, '立即打开')]/../../preceding-sibling::*[1]") 
                            
                    if "奖励已领取" in elements[0].text:
                        self.log("✅ 广告观看完成")
                        if self.d(textContains="跳过").exists:
                            click_by_xpath_text(self.d, "跳过")
                        elif self.d(textContains="反馈").exists:
                            self.log("🗨️ 发现反馈弹窗，点击取消")
                            click_by_xpath_text(self.d, xpaths="//*[contains(@text, '反馈')]/../following-sibling::*[1]")
                        else:
                            self.d.press("back")# 什么也找不到就点击退出
                            
                    if "进入微信" in elements[0].text:
                        self.log(" 遇见最难处理的弹框")
                        if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '提前拿奖励')]/../../preceding-sibling::*[1]//android.widget.ImageView"):
                            time.sleep(random.uniform(1, 3))
                        elif click_by_xpath_text(self.d, "跳过"):
                            time.sleep(random.uniform(1, 3))
                        click_by_xpath_text(self.d, ["坚持退出","立即退出"])
                        continue
                        
                    if "完成App下载" in elements[0].text: 
                        self.log("🗨️ 发现-下载-弹窗")
                        if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '完成App下载')]/../../preceding-sibling::*[1]/*[1]/*[2]//android.widget.ImageView"):
                            time.sleep(random.uniform(1, 3))
                            if click_by_xpath_text(self.d, "去下载拿奖励"):
                                time.sleep(random.uniform(1, 3))
                                if self.d.xpath('//*[@text="恭喜获得奖励"]').exists:
                                    pass
                                elif self.d.xpath('//*[contains(@text, "安装")]').exists:
                                    time.sleep(random.uniform(1, 3))
                                    self.d.app_start("com.ucmobile.lite")
                            if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '恭喜获得奖励')]/../../preceding-sibling::*[1]/*[1]/*[2]//android.widget.ImageView"):
                                time.sleep(random.uniform(1, 3))
                            
                    if "完成App安装" in elements[0].text:
                        if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '完成App安装')]/../../preceding-sibling::*[1]/*[1]/*[1]//android.widget.ImageView"):
                            time.sleep(random.uniform(1, 3))
                            if click_by_xpath_text(self.d, "去安装拿奖励"):
                                if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '恭喜获得奖励')]/../../preceding-sibling::*[3]/*[3]/*[1]/*[1]//android.widget.ImageView"):
                                    time.sleep(random.uniform(1, 3))

                    if "恭喜获得奖励" in elements[0].text: 
                        self.log("🗨️ 发现-恭喜获得奖励-弹窗")    
                        click_by_xpath_text(self.d, xpaths="//*[contains(@text, '恭喜获得奖励')]/../following-sibling::*[1]//android.widget.ImageView")
                
                if self.d(textContains="反馈").exists:
                    if self.d(textContains="反馈").exists and self.d(textContains="秒可立即").exists:
                        pass
                    else:
                        self.log("🗨️ 发现反馈弹窗，点击取消")
                        if self.d(textContains="加速领奖").exists:
                            self.log("✅ 发现加速弹框")
                            click_by_xpath_text(self.d, xpaths="//*[contains(@text, 'svg%3e')]")
                        elif self.d(textContains="跳过").wait_gone(timeout=35):
                            click_by_xpath_text(self.d, xpaths="//*[contains(@text, '反馈')]/../following-sibling::*[1]")

                vc.set_targets(["奖励已到账", "我要加速领奖", "直接拿奖励", "可立即领奖"])
                matched_text = vc.match_text()  # 会识别屏幕上的按钮文本，并缓存结果
                if matched_text == "奖励已到账":
                    self.log("✅ 发现奖励已到账")
                    vc.find_and_click()  # 会用 match_text 缓存的 OCR 结果点击“奖励已到账”按钮
                elif matched_text in ["我要加速领奖", "可立即领奖"]:
                    self.log("✅ 发现加速弹框")
                    click_by_xpath_text(self.d, xpaths="//*[contains(@text, 'svg%3e')]")
                elif matched_text == "直接拿奖励":
                    self.log("✅ 发现直接拿奖励弹框")
                    vc.find_and_click()  # 点击“直接拿奖励”按钮
                    self.d.app_start("com.ucmobile.lite")
                    self.d.press("back")
                elif matched_text == "去支付宝":
                    self.log("✅ 发现去支付宝")
                    self.d.press("back")
                    click_by_xpath_text(self.d, xpaths="//*[@text='首页']/../../*[5]//android.widget.ImageView")
    
                if self.d.xpath('//*[contains(@text, "继续观看")]').exists:
                    self.log_debug("🗨️ 发现-继续观看-弹窗")
                    click_by_xpath_text(self.d, "继续观看")
                    if self.d(text="跳过").exists:
                        self.log("✅ 发现跳过按钮")
                        if self.d(textContains="跳过").wait_gone(timeout=20):
                            self.log("✅ 跳过按钮已消失")
                            time.sleep(random.uniform(1, 3))
                            self.d.press("back")
                    else:
                        click_by_xpath_text(self.d, "可直接领奖")
                        
                if self.d(textContains="添加到主屏幕").exists:
                    ph.check_and_handle_popup()    
                        
                if self.d.xpath('//*[@resource-id="app"]').exists:
                    self.log_debug("🗨️ 发现-APP-弹窗")
                    self.d.press("back")
                
                vc.set_targets(["看视频再得"])
                matched_text = vc.match_text()
                if matched_text == "看视频再得":
                    vc.find_and_click()
                    continue
                
                vc.set_targets(["现金余额"])
                matched_text = vc.match_text()
                if matched_text == "现金余额" and time.time() - start_time > 30:
                    self.log("✅ 全部任务已完成，返回首页")
                    return True
                else:
                    time.sleep(check_interval)

            except Exception as e:
                self.log_error(f"❌ 广告监控出错: {e}")
                time.sleep(check_interval)

        self.log("⏰ 广告观看超时")
        return False
