import time, cv2, re, os
import numpy as np
from cnocr import CnOcr
from appium import webdriver
from typing import List, Dict, Tuple
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class AppiumSmartController:
    def __init__(self):
        # 初始化OCR检测器
        self.ocr_detector = UIElementsDetector()
        
        # Appium配置
        self.options = UiAutomator2Options()
        self.options.platform_name = "Android"
        self.options.device_name = "9a5dbfaf"  
        self.options.app_package = "com.ss.android.ugc.aweme.lite"
        self.options.app_activity = "com.ss.android.ugc.aweme.main.MainActivity"
        self.options.no_reset = True
        
        # 启动驱动
        self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", options=self.options)
        self.screen_size = self.driver.get_window_size()
        
    def precise_tap(self, x, y, adjust_status_bar=True):
        """
        使用W3C标准Actions精准点击坐标（可选状态栏偏移校准）
        
        :param x: 横坐标（像素）
        :param y: 纵坐标（像素）
        :param adjust_status_bar: 是否自动调整状态栏偏移（默认True）
        :raises: RuntimeError 如果点击失败
        """
        try:
            target_y = y
            
            # 仅在需要时计算状态栏偏移
            if adjust_status_bar:
                screen_height = self.driver.get_window_size()['height']
                status_bar_height_ratio = 0.06  # 假设状态栏占屏幕高度的5%
                target_y = y + int(status_bar_height_ratio * screen_height)
                print(f"📊 已应用状态栏偏移校准: y={y} → {target_y}")

            # 执行精准点击
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(x, target_y)
            actions.w3c_actions.pointer_action.click()
            actions.perform()
            
            print(f"✅ 已点击坐标 ({x}, {target_y}) [状态栏校准: {'是' if adjust_status_bar else '否'}]")
            
        except WebDriverException as e:
            self.driver.save_screenshot('tap_failed.png')
            raise RuntimeError(f"坐标点击失败: {str(e)}\n错误截图已保存为 tap_failed.png")
    
   
    def smart_click(self, target_text: str, timeout: int = 10, retry: int = 3):
        """智能点击：通过OCR识别文本并点击对应元素"""
        for attempt in range(retry):
            try:
                # 获取当前脚本所在目录
                current_dir = os.path.dirname(os.path.abspath(__file__))
                screenshot_path = os.path.join(current_dir, f"temp_screen_{attempt}.png")

                self.driver.save_screenshot(screenshot_path)
                # 2. 检测所有可点击元素
                elements = self.ocr_detector.detect_clickable_elements(screenshot_path)
                
                # 3. 查找匹配的按钮
                matched_btns = [btn for btn in elements['buttons'] 
                                if target_text in btn['text']]
                
                if not matched_btns:
                    print(f"第{attempt+1}次尝试：未找到包含'{target_text}'的按钮")
                    time.sleep(2)
                    continue
                
                # 4. 选择最可能的按钮
                target_btn = matched_btns[0]
                x = int(target_btn['center'][0] * self.screen_size['width'])
                y = int(target_btn['center'][1] * self.screen_size['height'])
                
                # 5. 执行点击
                self.precise_tap(x, y)
                print(f"成功点击：'{target_text}' (坐标: {x},{y})")
                return True
                
            except Exception as e:
                print(f"第{attempt+1}次尝试失败：{str(e)}")
                time.sleep(1)
        
        print(f"⚠️ 重试{retry}次后仍未找到'{target_text}'")
        return False

    def detect_clickable_elements(self, screenshot_path: str) -> Dict[str, List[Dict]]:
        """检测图片中所有可点击元素及其位置
        
        Returns:
            {
                "buttons": [{"text": "去提现", "bbox": [x1,y1,x2,y2]}...],
                "key_texts": [{"text": "815金币", "bbox": [...]}...]
            }
        """
        img = cv2.imread(screenshot_path)
        if img is None:
            raise ValueError("无法读取图片")
            
        # 获取OCR结果带位置信息
        ocr_results = self.ocr.ocr(img)
        
        # 分析布局
        elements = self._analyze_elements(ocr_results, img.shape)
        
        return elements
    
    def _analyze_elements(self, ocr_results: List[Dict], img_shape: Tuple[int]) -> Dict:
        """分析OCR结果，识别按钮和关键文本"""
        h, w = img_shape[:2]
        
        buttons = []
        key_texts = []
        
        # 按钮特征：包含动作词且通常位于底部或右侧
        button_keywords = ['去', '点击', '领取', '提现', '签到', '预约', '打卡', '登录', '看广告', '逛街赚钱', '看视频赚金币']
        
        for res in ocr_results:
            text = res['text'].strip()
            if not text:
                continue
                
            # 获取边界框坐标 (x1,y1,x2,y2)
            bbox = self._get_normalized_bbox(res['position'], w, h)
            
            # 识别按钮
            if any(keyword in text for keyword in button_keywords):
                buttons.append({
                    "text": text,
                    "bbox": bbox,
                    "center": self._get_center(bbox)
                })
            # 识别关键数值
            elif re.search(r'\d+\.?\d*(金币|现金|天|万)', text):
                key_texts.append({
                    "text": text,
                    "bbox": bbox,
                    "center": self._get_center(bbox)
                })
        
        return {
            "buttons": buttons,
            "key_texts": key_texts
        }
    
    def _get_normalized_bbox(self, positions: List[List[int]], img_w: int, img_h: int) -> List[int]:
        """将OCR返回的多边形框转为标准矩形框(x1,y1,x2,y2)并归一化"""
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        return [
            max(0, min(xs)/img_w),    # x1 (0~1)
            max(0, min(ys)/img_h),    # y1 (0~1)
            min(1, max(xs)/img_w),    # x2 (0~1)
            min(1, max(ys)/img_h)     # y2 (0~1)
        ]
    
    def _get_center(self, bbox: List[float]) -> Tuple[float, float]:
        """计算bbox中心点坐标(归一化)"""
        return ((bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2)        


# class renwu():
#     def __init__(self):
#         # renwulei = AppiumSmartController()
        
        
#     def qiandao(self, x, y):
#         """点击签到按钮"""
#         self.renwulei.precise_tap(x, y)
        
    
# 使用示例
if __name__ == "__main__":
    
    def close_popup_via_adb():
        os.system("adb shell input keyevent KEYCODE_BACK")
    controller = AppiumSmartController()
    # detector = UIElementsDetector()
    # zhurenwu = renwu()com.ss.android.ugc.aweme.lite:id/d7y
    # 点击福袋
    controller.click_btn("accessibility id", "福袋", "福袋")
    time.sleep(5)
    controller.click_btn("xpath", '//*[contains(@text, "看视频")]', "看视频")
    controller.click_btn("xpath", '//*[contains(@text, "提醒我")]', "提醒我")
    controller.click_btn("xpath", '//*[contains(@text, "去领取")]', "去领取")
    controller.click_btn("xpath", '//*[contains(@text, "去打卡")]', "去打卡")
    controller.click_btn("xpath", '//*[contains(@text, "打卡领五粮液")]', "打卡领五粮液")
    # if controller.smart_click("登录"):
    #     print("已成功点击登录按钮")
    #     controller.denglu()
    #     time.sleep(5)
    
    # # 示例2：OCR智能点击
    controller.smart_click("去签到")
    time.sleep(3)
    controller.precise_tap(539, 1672, adjust_status_bar=False)  # 点击签到按钮
    close_popup_via_adb()
    
    controller.smart_click("去预约")
    controller.click_btn("text", "立即预约领取", "立即预约领取")
    controller.click_btn("text", "提醒我来领", "提醒我来领")
    
    controller.smart_click("已打卡")
    # controller.click_btn("text", "点击打卡", "点击打卡")
    time.sleep(3)
    close_popup_via_adb()
    
    controller.smart_click("看广告赚金币")
    controller.click_btn("text", "看指定视频领晚餐补贴", "看指定视频领晚餐补贴")
    controller.click_btn("text", "领取奖励", "领取奖励")
    daotime = controller.wait_for_element("xpath", "//*[contains(@content-desc, '可领奖励，关闭，按钮')]").get_attribute("content-desc")
    print(f"等待时间: {daotime}")
    
    controller.smart_click("看广告赚金币")
    while True: 
        daotime = controller.wait_for_element("xpath", "//*[contains(@content-desc, '关闭，按钮')]").get_attribute("content-desc")
        print(f"等待时间: {daotime}")
        time.sleep(3)
        if "领取成功" in daotime:
            controller.click_btn("xpath", "//*[contains(@content-desc, '关闭，按钮')]", "可领奖励，关闭，按钮")
            break              
    controller.click_btn("text", "领取成功，关闭，按钮", "领取成功，关闭，按钮")
    controller.click_btn("text", "领取奖励", "领取奖励")
    
    def swipe_up_simple(driver, duration=1000):
        """直接使用 swipe 方法"""
        screen = driver.get_window_size()
        driver.swipe(
            start_x=screen["width"] // 2,
            start_y=screen["height"] * 0.8,
            end_x=screen["width"] // 2,
            end_y=screen["height"] * 0.2,
            duration=duration
        )
    
    controller.smart_click("逛街赚钱")
    time.sleep(3)
    while True:
        swipe_up_simple(controller.driver)
        time.sleep(3)
        while True: 
            daotime = controller.wait_for_element("xpath", "//*[contains(@text, '秒')]").get_attribute("content-desc")
            print(f"等待时间: {daotime}")
        评价并收下金币
    
    
    # controller.smart_click("看视频赚金币")
    # # controller.click_btn("text", "领取成功，关闭，按钮", "领取成功，关闭，按钮")
    # # controller.click_btn("text", "领取奖励", "领取奖励")
    # while True: 
    #     daotime = controller.wait_for_element("xpath", "//android.widget.TextView[contains(@text, '已看')]").get_attribute("text")
    #     print(daotime)
    #     # 先按 "已看" 分割，再按 "/" 分割
    #     number = daotime.split("已看")[1].split("/")[0]
    #     number1 = daotime.split("已看")[1].split("/")[1]
    #     print(number)  # 输出: "8"
    #     print(number1)
    #     if number == number1:
    #         controller.click_btn("xpath", "//android.widget.TextView[contains(@content-desc, '可领奖励，关闭，按钮')]", "可领奖励，关闭，按钮")
    #         break
    #     swipe_up_simple(controller.driver)
    #     time.sleep(3)