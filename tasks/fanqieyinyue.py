import time
from utils.tools import *
import uiautomator2 as u2
from ad_handler.fanqieyinyue_handler import FanQieYinYueAdWatcher
from logger import log
from Image_elements.visual_clicker import *
from utils.taskmanager import TaskManager

def run(d: u2.Device):
    try:
        app_name = "番茄音乐"
        log(f"[{d.serial}] 启动 {app_name} 任务")
        d.app_start("com.xs.fm.lite")
        time.sleep(10)
        aw = FanQieYinYueAdWatcher(d)
        tm = TaskManager(d, app_name)
        vc = VisualClicker(d)
        click_by_xpath_text(d, xpaths="(//android.widget.Button)[2]")  
        print("点击暂停")
        click_by_xpath_text(d, "领现金")
        
        def task_daily_checkin():
            if wait_exists(d.xpath('//*[contains(@text, "新人礼加送现金")]')):
                print("🗨️ 发现-新人送现金-弹窗")
                click_by_xpath_text(d, "领取今日现金")
        tm.run_task_once("新人送现金", task_daily_checkin)
        
        def task_daily_checkin():
            # 判断是否存在抽奖弹窗
            vc.set_targets(["立即前往"])
            matched_text = vc.match_text()
            if matched_text == "立即前往": 
                vc.click_by("立即前往")
                if vc.click_by("去抽奖"):
                    if vc.click_by("看视频再抽一次"):
                        aw.watch_ad()
                    elif vc.click_by("活动繁忙"):
                        d.press("back")
                        print("活动繁忙，点击后退...")
        tm.run_task_once("抽奖任务", task_daily_checkin)      
        
        def task_daily_checkin():      
            vc.set_targets(["今日签到"])
            matched_text = vc.match_text()
            if matched_text == "今日签到":
                print("🗨️ 发现-今日签到-弹窗")
                if click_by_xpath_text(d, "立即签到"):
                    if click_by_xpath_text(d, "看视频再领"):
                        aw.watch_ad()
        tm.run_task_once("今日签到", task_daily_checkin)
        
        def task_daily_checkin():
            vc.set_targets(["去赚更多", "立即签到"])
            matched_text = vc.match_text()
            if matched_text == "去赚更多":
                pass
            elif matched_text == "立即签到":
                if click_by_xpath_text(d, "签到领现金"):
                    click_by_xpath_text(d, ["继续赚金币", "明日再来"])
        tm.run_task_once("赚金币", task_daily_checkin)
        
        if click_by_xpath_text(d, "开宝箱得金币"):
            if click_by_xpath_text(d, "看视频再得"):
                aw.watch_ad()
        
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出      
    finally:
        log(f"[{d.serial}] 番茄音乐 任务完成")
        d.app_stop("com.xs.fm.lite")