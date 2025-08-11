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
            "我要加速领奖",
            "去体验15秒可立即领奖",
            "长按加速视频"
            
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

                    # 这里先删掉 any(t in elements[0].text for t in [""]) 这句无用判

                    if "奖励已领取" in elements[0].text:
                        self.log("✅ 广告观看完成")
                        if click_by_xpath_text(self.d, "跳过"):
                            if self.d(textContains="反馈").exists:
                                self.log("🗨️ 发现反馈弹窗，点击取消")
                                click_by_xpath_text(self.d, xpaths="//*[contains(@text, '反馈')]/../following-sibling::*[1]//android.widget.ImageView")
                            
                            self.log_debug("识别看视频再得")
                            vc.set_targets(["看视频再得"])
                            matched_text = vc.match_text()
                            if matched_text == "看视频再得":
                                vc.find_and_click()
                                continue
                    
                    if "长按加速视频" in elements[0].text:
                        self.log("✅ 发现长按加速视频弹框")
                        long_press_until_gone(
                            self.d,
                            press_xpath='//*[@text="长按加速视频"]/../..//android.widget.ImageView',
                            wait_xpath='//*[@text="立即获取"]',
                            timeout=20,
                            release_delay=0.5
                        )   
                    
                    if "我要加速领奖" in elements[0].text:
                        self.log("✅ 发现加速弹框")
                        if click_by_xpath_text(self.d, xpaths="//*[contains(@text, 我要加速领奖)]/../../../following-sibling::*[2]//android.widget.Image"):
                            continue
                        
                    if "去体验15秒可立即领奖" in elements[0].text:
                        self.log("✅ 发现去体验立即领奖弹框")
                        if click_by_xpath_text(self.d, "跳过"):
                            time.sleep(random.uniform(1, 3))
                            click_by_xpath_text(self.d, "坚持退出")
                            
                    if "进入微信" in elements[0].text:
                        self.log(" 遇见最难处理的弹框")
                        if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '提前拿奖励')]/../../preceding-sibling::*[1]//android.widget.ImageView"):
                            time.sleep(random.uniform(1, 3))
                        elif click_by_xpath_text(self.d, "跳过"):
                            time.sleep(random.uniform(1, 3))
                        click_by_xpath_text(self.d, ["坚持退出","立即退出"])
                        continue
                        
                    if "完成App下载" in elements[0].text or "完成App安装" in elements[0].text: 
                        self.log("🗨️ 发现-下载-弹窗")
                        if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '完成App下载')]/../../preceding-sibling::*[1]/*[1]/*[2]//android.widget.ImageView"):
                            time.sleep(random.uniform(1, 3))
                        elif click_by_xpath_text(self.d, xpaths="//*[contains(@text, '完成App安装')]/../../preceding-sibling::*[1]/*[1]/*[1]//android.widget.ImageView"):
                            time.sleep(random.uniform(1, 3))
                        if click_by_xpath_text(self.d, ["去下载拿奖励", "去安装拿奖励"]):
                            time.sleep(random.uniform(1, 3))
                            if self.d.xpath('//*[@text="恭喜获得奖励"]').exists:
                                pass
                            elif self.d.xpath('//*[@text="腾讯元宝"]').exists:
                                click_by_xpath_text(self.d, "立即下载")
                                time.sleep(random.uniform(1, 3))
                                self.d.app_start("com.ucmobile.lite")
                        
                            if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '完成App下载')]/../../preceding-sibling::*[1]/*[1]/*[2]//android.widget.ImageView"):
                                 time.sleep(random.uniform(1, 3))
                            elif click_by_xpath_text(self.d, xpaths="//*[contains(@text, '恭喜获得奖励')]/../../preceding-sibling::*[3]/*[3]/*[1]/*[1]//android.widget.ImageView"):
                                time.sleep(random.uniform(1, 3))
                            
                            self.log_debug("识别看视频再得")
                            vc.set_targets(["看视频再得"])
                            matched_text = vc.match_text()
                            if matched_text == "看视频再得":
                                vc.find_and_click()
                                continue
                                
                        if click_by_xpath_text(self.d, xpaths="//*[contains(@text, '完成App安装')]/../../preceding-sibling::*[1]/*[1]/*[2]//android.widget.ImageView"):
                            time.sleep(random.uniform(1, 3))
                            
                    if "恭喜获得奖励" in elements[0].text: 
                        self.log("🗨️ 发现-恭喜获得奖励-弹窗")    
                        click_by_xpath_text(self.d, xpaths="//*[contains(@text, '恭喜获得奖励')]/../following-sibling::*[1]//android.widget.ImageView")
                
                if self.d(text="跳过").exists:
                    self.log("✅ 发现跳过按钮")
                    if self.d(textContains="s").wait_gone(timeout=35):
                        pass
                        
                        
                    
                vc.set_targets(["奖励已到账", "去支付宝"])
                matched_text = vc.match_text()
                if matched_text == "奖励已到账":
                    self.log("✅ 发现奖励已到账")
                    vc.find_and_click()
                elif matched_text == "去支付宝":
                    self.log("✅ 发现去支付宝")
                    self.d.press("back")
                    click_by_xpath_text(self.d, xpaths="//*[@text='首页']/../../*[5]//android.widget.ImageView", wait_gone=False)
                    
                self.log_debug("识别看视频再得")
                vc.set_targets(["看视频再得"])
                matched_text = vc.match_text()
                if matched_text == "看视频再得":
                    vc.find_and_click()
                    continue
                    
                if self.d(textContains="添加到主屏幕").exists:
                        ph.check_and_handle_popup()          
                if self.d.xpath('//*[@resource-id="app"]').exists:
                    self.log_debug("🗨️ 发现-APP-弹窗")
                    self.d.press("back")

                vc.set_targets(["现金余额"])
                matched_text = vc.match_text()
                if matched_text == "现金余额" and time.time() - start_time > 30:
                    self.log("✅ 全部任务已完成，返回首页")
                    return True

                time.sleep(check_interval)

            except Exception as e:
                self.log_error(f"❌ 广告监控出错: {e}")
                time.sleep(check_interval)

        self.log("⏰ 广告观看超时")
        return False
