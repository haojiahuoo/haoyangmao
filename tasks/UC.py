import time, random, re
import uiautomator2 as u2
from utils.tools import *
from logger import log, log_error, log_debug
from Image_elements.visual_clicker import VisualClicker
from ad_handler.UC_handler import UCAdWatcher
from Image_elements.ocr_helper import SmartController
from utils.taskmanager import TaskManager

def run(d: u2.Device):
    
    app_name = "UC浏览器"
    log(f"[{d.serial}] 启动 {app_name} 任务")
    d.app_start("com.ucmobile.lite")
    vc = VisualClicker(d)
    aw = UCAdWatcher(d)
    tm = TaskManager(d, app_name)
    time.sleep(10)
    try:
        time.sleep(5)
        log_debug("开始识别各种弹窗...")
        vc.set_targets(["周年福利"])
        matched_text = vc.match_text()
        if matched_text == "周年福利":
            log_debug("识别周年福利")
            d.press("back")  # 返回上一页
            
        # 进入任务页面
        if click_by_xpath_text(d, xpaths="//*[@text='首页']/../../*[5]//android.widget.ImageView"):
        
            def task_daily_checkin():
                vc.set_targets(["看激励视频", "施肥可得"])
                matched_text = vc.match_text()
                if matched_text == "看激励视频":
                    vc.find_and_click()
                    aw.watch_ad()
                elif matched_text == "施肥可得":
                    time.sleep(random.uniform(1, 3))  # 等待1-3秒
                    d.click(925, 783)  # 点击屏幕中心
            tm.run_task_once("每日弹窗", task_daily_checkin)
        
            log_debug("识别是否进入任务页面...")
            vc.set_targets(["现金余额"])
            matched_text = vc.match_text()
            if matched_text == "现金余额":
                log("⏳ 等待10秒让网页稳定....")
                time.sleep(10)
                log("✅ 加载完成，开始工作")
                
            log_debug("识别开宝箱任务...")
            vc.set_targets(["开宝箱"])
            matched_text = vc.match_text()
            if matched_text == "开宝箱": 
                if vc.find_and_click():
                    vc.set_targets(["看视频再"])
                    matched_text = vc.match_text()
                    if matched_text == "看视频再":
                        vc.find_and_click()
                        aw.watch_ad()  
            
            vc.set_targets(["领元宝"])
            matched_text = vc.match_text()
            if matched_text == "领元宝":
                start_time = time.time()
                while time.time() - start_time < 12000:  # 最多等待60秒
                    matched_text = vc.match_text(return_full_text=True)
                    if matched_text and "领元宝" in matched_text:
                        numbers = re.sub(r'\D', '', matched_text)  
                        group1 = numbers[:-2] if len(numbers) > 2 else ""  
                        group2 = numbers[-2:]  # "35"
                        if group1 >= group2:
                            log("✅ 还没满，执行点击")
                            if vc.find_and_click(target="领元宝"):
                                aw.watch_ad()
                        else:
                            log("⚠️ 已满或无法提取数字")
                            break
                    else:
                        log("❌ 找不到按钮")
                        break
                log("✅ 时间太长了，别再看了...")
            
                    
    except Exception as e:
        log_error(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出      
    finally:
        vc.set_targets(["现金余额"])
        matched_text = vc.match_text(return_full_text=True)
        if "现金余额" in matched_text:
            xianjin_text = matched_text
        vc.set_targets(["元宝"])
        matched_text = vc.match_text(return_full_text=True)
        if "元宝" in matched_text:    
            jinbi_text = matched_text
            
        jinbi_value = float(re.sub(r'[^\d.]', '', jinbi_text))
        xianjin_value = float(re.sub(r'[^\d.]', '', xianjin_text))
        print(f"{app_name} 收益已记录: 金币={jinbi_value}, 现金={xianjin_value}")
        
        log(f"[{d.serial}] UC浏览器 任务完成")
        d.app_stop("com.ucmobile.lite")
        return jinbi_value, xianjin_value