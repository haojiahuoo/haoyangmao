import time, random, re
import uiautomator2 as u2
from utils.tools import *
from logger import log, log_error, log_debug
from Image_elements.visual_clicker import VisualClicker
from ad_handler.hongguo_handier import HongGuoAdWatcher
from Image_elements.ocr_helper import SmartController
from utils.taskmanager import TaskManager

def run(d: u2.Device):
    
    app_name = "红果免费短剧"
    log(f"[{d.serial}] 启动 {app_name} 任务")
    d.app_start("com.phoenix.read")
    vc = VisualClicker(d)
    aw = HongGuoAdWatcher(d)
    tm = TaskManager(d, app_name)
    time.sleep(10)
    try:
        click_by_xpath_text(d, "赚钱")
        
    #---------------- 每日执行一次的任务 ----------------
        #------------弹窗的处理 ----------------  
        vc.set_targets(["领取今日现金"])
        matched_text = vc.match_text()
        if matched_text == "领取今日现金":
            log("🗨️ 发现-领取今日现金-弹窗")
            if vc.find_and_click():
                vc.set_targets(["明日签到"])
                matched_text = vc.match_text()
                if matched_text == "领取今日现金":
                    log("🗨️ 发现-领取今日现金-弹窗")
                    vc.find_and_click()
            
        def task_daily_checkin():
            if d(textContains="获得预约礼包").exists:
                print("🗨️ 发现-预约礼包-弹窗")
                if click_by_xpath_text(d, "立即领取"):
                    time.sleep(random.uniform(1, 3))
                    click_by_xpath_text(d, "一键领取")
                    time.sleep(random.uniform(1, 3))
                    if click_by_xpath_text(d, "看视频再"):
                        aw.watch_ad()
                        click_by_xpath_text(d, "继续预约")
                        time.sleep(random.uniform(1, 3))
                        click_by_xpath_text(d, "我知道了")
                        time.sleep(random.uniform(1, 3))
                        d.press("back")
        tm.run_task_once("获得预约礼包", task_daily_checkin)
        
        #--------------日常任务------------------
        # if d(textContains="一大波红包").exists:
        #     log("🗨️ 发现-一大波红包-弹窗")
        #     click_by_xpath_text(d, "金币红包雨")
        #     time.sleep(10)
        #     if click_by_xpath_text(d, "看视频翻倍领取"):
        #         aw.watch_ad()
        
        
        log("⏳识别-宝箱任务")
        if click_by_xpath_text(d, ["点击领", "开宝箱"]):
            time.sleep(random.uniform(1, 3))
            click_by_xpath_text(d, "看视频最高")
            aw.watch_ad() 
        
        # log("点击看短剧任务")
        # click_by_xpath_text(d, "看短剧赚金币")   
    
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出      
    finally:
        time.sleep(5)
        text = d.xpath('//*[contains(@text, "金币收益")]/following-sibling::*[1]').text
        log(f"识别到文本: {text}")
        jinbi_text = re.search(r'金币收益(\d+)', text).group(1)
        jinbi_value = float(re.sub(r'[^\d.]', '', jinbi_text))
            
        text = d.xpath('//*[contains(@text, "现金收益")]/following-sibling::*[1]').text
        log(f"识别到文本: {text}")
        xianjin_text = re.search(r'现金收益([\d.]+)', text).group(1)
        xianjin_value = float(re.sub(r'[^\d.]', '', xianjin_text))
        log(f"{app_name} 收益已记录: 金币={jinbi_value}, 现金={xianjin_value}")
        log(f"[{d.serial}] {app_name} 任务完成")
        d.app_stop("com.phoenix.read")
    return jinbi_value, xianjin_value 