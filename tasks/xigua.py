import time, random, re
import uiautomator2 as u2
from utils.tools import *
from Image_elements.visual_clicker import VisualClicker
from ad_handler.xigua_handler import XiGuaAdWatcher
from logger import log
from utils.taskmanager import TaskManager

def run(d: u2.Device):
    try:
        app_name = "西瓜视频"
        log(f"[{d.serial}] 启动 {app_name}")
        d.app_start("com.ss.android.article.video")
        time.sleep(10)
        
        vc = VisualClicker(d)
        aw = XiGuaAdWatcher(d)
        tm = TaskManager(d, app_name)
        
        click_by_xpath_text(d, "我的")
        time.sleep(random.uniform(1, 3))
        click_by_xpath_text(d, "去赚现金")
        
        vc.set_targets(["金币收益"])
        matched_text = vc.match_text()
        if matched_text == "金币收益":
            print("⏳ 等待10秒让网页稳定....")
            time.sleep(10)
            print("✅ 加载完成，开始工作")
            
# ---------------- 每日执行一次的任务 ----------------
            # ------------弹窗的处理 ----------------  
            
            def task_daily_checkin():
                print("⏳ 开始识别[签到7天领金币]弹窗")
                if vc.click_by("立即签到+"):
                    if vc.click_by("看广告视频"):
                        aw.watch_ad()
            tm.run_task_once("[签到7天领金币]弹窗", task_daily_checkin)
            
            def task_daily_checkin():
                print("⏳ 开始识别[开宝箱奖励]弹窗")
                if vc.click_by("看广告视频"):
                    aw.watch_ad()
            tm.run_task_once("[开宝箱奖励]弹窗", task_daily_checkin)
            
            def task_daily_checkin():        
                print("⏳ 开始识别[预约领金币]弹窗")
                vc.set_targets(["预约领金币"])
                matched_text = vc.match_text()
                if matched_text  == "预约领金币":
                    if click_by_xpath_text(d, "立即领取"):
                        print("✅ 开始领取流程")
                        click_by_xpath_text(d, "一键领取")
                        click_by_xpath_text(d, "开心收下")
                        click_by_xpath_text(d, "立即预约领取")
                        click_by_xpath_text(d, "提醒我来领")
                        if click_by_xpath_text(d, "领取奖励"):
                            aw.watch_ad()
                        d.press("back")
                else:
                    print("⚠️ 未匹配到任何目标文本")
            tm.run_task_once("[预约领金币]弹窗", task_daily_checkin)    
    
        # ------------日常任务的处理 ----------------  
        
            vc.set_targets(["日常任务"])
            matched_text = vc.match_text()
            pos =  vc.find_and_click()
            if pos:
                x, y = pos
                # 拖动到顶部（比如 y=100）
                d.swipe(x, y, x, 650, 0.3)
            
            # 签到预约领金币
            def task_daily_checkin():
                print("⏳ 开始识别[预约领金币]")
                vc.set_targets(["今日预约", "24点前", "明日0点", "明日11点"])
                matched_text = vc.match_text()
                if matched_text in ["明日0点", "明日11点"]:
                    print("✅ 明天再来！")
                elif matched_text in ["今日预约", "24点前"]:
                    print("✅ 开始领取流程")
                    vc.find_and_click()
                    click_by_xpath_text(d, ["立即预约领取", "一键领取"])
                    click_by_xpath_text(d, "开心收下")
                    click_by_xpath_text(d, "立即预约领取")
                    click_by_xpath_text(d, "提醒我来领")
                    click_by_xpath_text(d, "领取奖励")
                    aw.watch_ad()
                    d.press("back")
                else:
                    print("⚠️ 未匹配到任何目标文本")
            tm.run_task_once("签到预约领金币", task_daily_checkin)
            
            # 点击领宝箱
            print('⏳ 开始识别[宝箱任务]')
            vc.set_targets(["点击领", "开宝箱"])
            matched_text = vc.match_text()
            print("🧾 识别结果:", repr(matched_text)) 
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
            
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出
    finally:
        d.press("back")
        time.sleep(1)
        if d(textContains="去赚现金").exists:
            time.sleep(1)
            jinbi_text = d(resourceId="com.ss.android.article.video:id/ep3").get_text() or "0"
            jinbi_value = float(re.sub(r'[^\d.]', '', jinbi_text))
        
            xianjin_text = d(resourceId="com.ss.android.article.video:id/ep7").get_text() or "0"
            xianjin_value = float(re.sub(r'[^\d.]', '', xianjin_text))
            
            print(f"{app_name} 收益已记录: 金币={jinbi_value}, 现金={xianjin_value}")
            log(f"[{d.serial}] 西瓜视频 任务完成")
            d.app_stop("com.ss.android.article.video")
        return jinbi_value, xianjin_value
