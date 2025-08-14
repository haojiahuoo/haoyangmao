import time, os, random
from utils.tools import *
import uiautomator2 as u2
from Image_elements.visual_clicker import VisualClicker
from ad_handler.douyin_handler import DouYinAdWatcher
from logger import log
from utils.taskmanager import TaskManager

def run(d: u2.Device):
    try:
        log(f"[{d.serial}] 启动 抖音极速版")
        d.app_start("com.ss.android.ugc.aweme.lite")
        time.sleep(10)
        tm = TaskManager(d, "com.ss.android.ugc.aweme.lite")
        vc = VisualClicker(d)
        aw = DouYinAdWatcher(d)
        
        if wait_exists(d(textContains="首页")):
            d.xpath("//android.widget.TabHost/android.widget.FrameLayout[2]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.ImageView[2]").click()
        
        vc.set_targets(["金币收益"])    
        matched_text = vc.match_text()
        if matched_text == "金币收益":
            log("⏳ 等待15秒让网页稳定....")
            time.sleep(15)
            log("✅ 加载完成，开始工作")

# ---------------- 每日执行一次的任务 ----------------
            # ------------弹窗的处理 ----------------
            def task_daily_checkin():
                log("识别已连续签到")
                vc.set_targets(["签到领"])
                matched_text = vc.match_text()
                if matched_text == "签到领":
                    vc.find_and_click()
                    log("✅ 点击--签到领")
                    time.sleep(2)
                    vc.set_targets(["看广告", "开心收下", "好的", "最高得"])
                    matched_text = vc.match_text()
                    if matched_text in ["开心收下", "好的"]:
                        vc.find_and_click()
                    elif matched_text == "最高得":
                        d.press("back")
                    elif matched_text == "看广告":
                        vc.find_and_click()
                        log("✅ 点击--看广告")
                        aw.watch_ad()
                else:
                    log('⚠️ ["签到领"]未匹配到任何目标文本')
            tm.run_task_once("新人签到", task_daily_checkin)

            def task_daily_checkin():
                log("⏳ 开始识别[预约领金币]弹窗")
                vc.set_targets(["预约领金币"])
                matched_text = vc.match_text()
                if matched_text  == "预约领金币":
                    if click_by_xpath_text(d, "立即预约领金币"):
                        log("✅ 开始领取流程")
                        click_by_xpath_text(d, "一键领取")
                        click_by_xpath_text(d, "开心收下")
                        click_by_xpath_text(d, "立即预约领取")
                        click_by_xpath_text(d, "提醒我来领")
                        if click_by_xpath_text(d, "领取奖励"):
                            aw.watch_ad()
                            d.press("back")
                else:
                    log('⚠️ ["预约领金币"]未匹配到任何目标文本') 
            tm.run_task_once("预约领金币", task_daily_checkin) 
        
            log("⏳ 开始识别[新人签到领大额金币]弹窗")
            vc.set_targets(["立即签到+"])
            matched_text = vc.match_text()
            if matched_text  == "立即签到+":
                vc.find_and_click()
                log("✅ 点击--立即签到+")
                time.sleep(1)
                log("✅ 识别明天再来")
                vc.set_targets(["明天再来"])
                if vc.find_and_click():
                    log("✅ 点击--明天再来")
            else:
                log('⚠️ ["立即签到+"]未匹配到任何目标文本')
            
            log("⏳ 开始识别[新人签到领金币]")
            vc.set_targets(["新人签到领金币"])
            matched_text = vc.match_text()
            if matched_text  == "新人签到领金币":
                vc.find_and_click()
                time.sleep(1)
                log("✅ 识别明天再来")
                vc.set_targets(["明天再来"])
                if vc.find_and_click():
                    log("✅ 点击--明天再来")
            else:
                log('⚠️ ["新人签到领金币"]未匹配到任何目标文本')

    # ------------日常任务的处理 ----------------

            vc.set_targets(["日常任务"])
            pos =  vc.find_and_click()
            if pos:
                x, y = pos
                # 拖动到顶部（比如 y=100）
                d.swipe(x, y, x, 650, 0.3)
    
            # 天天领金币
            log('⏳ 开始识别["明日签到立即", "今日签到立即"]')
            vc.set_targets(["明日签到立即", "今日签到立即"])
            matched_text = vc.match_text()
            if matched_text == "明日签到立即":
                log("⏳ 明天才能领取")
            elif matched_text == "今日签到立即":
                vc.find_and_click()
                time.sleep(random.uniform(1, 3))
                vc.set_targets(["今日可领"])
                time.sleep(random.uniform(1, 3))
                vc.find_and_click()
                time.sleep(random.uniform(1, 3))
                d.press("back")
            else:
                log("⚠️ 未匹配到任何目标文本")

            # 签到预约领金币
            log("⏳ 开始识别[预约领金币]")
            vc.set_targets(["今日预约", "24点前", "明日0点", "明日11点"])
            matched_text = vc.match_text()
            if matched_text in ["明日0点", "明日11点"]:
                log("✅ 明天再来！")
            elif matched_text in ["今日预约", "24点前"]:
                log("✅ 开始领取流程")
                vc.find_and_click()
                if click_by_xpath_text(d, "一键领取"):
                    click_by_xpath_text(d, "开心收下")
                    click_by_xpath_text(d, "立即预约领取")
                    click_by_xpath_text(d, "提醒我来领")
                    if click_by_xpath_text(d, "领取奖励"):
                        aw.watch_ad()
                    d.press("back")
            else:
                log("⚠️ 未匹配到任何目标文本")

                # 打卡领五粮液
            log('⏳ 开始识别["今日已打卡", "今日待打卡"]')
            vc.set_targets(["今日已打卡", "今日待打卡"])
            matched_text = vc.match_text()
            if matched_text == "今日已打卡":
                log("✅ 明天再来打卡")
            elif matched_text == "今日待打卡":
                vc.find_and_click()
                click_by_xpath_text(d, "点击打卡")
                time.sleep(5)
                d.press("back")
            else:
                log("⚠️ 未匹配到任何目标文本")

            

# ---------------- 每日日常执行的任务 ----------------      

            # 点击领宝箱
            log('⏳ 开始识别[宝箱任务]')
            vc.set_targets(["点击领", "开宝箱"])
            matched_text = vc.match_text()
            log("🧾 识别结果:", repr(matched_text)) 
            if matched_text in ["点击领", "开宝箱"]:
                vc.find_and_click()
                time.sleep(2)
                
                vc.set_targets(["看广告视频", "开心收下", "我知道了"])
                matched_text = vc.match_text()
                if matched_text == "看广告视频":
                    vc.find_and_click()
                    aw.watch_ad()
                elif matched_text in ["开心收下", "我知道了"]:
                    vc.find_and_click()
                    d.press("back")
            else:
                log("⚠️ 未匹配到任何目标文本")
                
            
            
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出      
    finally:
        log(f"[{d.serial}] 抖音极速版 任务完成")
        d.app_stop("com.ss.android.ugc.aweme.lite")





