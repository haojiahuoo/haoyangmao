import time
import uiautomator2 as u2
from utils.tools import *
from logger import log
from Image_elements.visual_clicker import VisualClicker
from ad_handler.wukong_handler import WuKongAdWatcher
from utils.taskmanager import TaskManager
from utils.revenuetracker import *

def run(d: u2.Device):
    try:
        app_name =  "悟空浏览器"
        log(f"[{d.serial}] 启动{app_name}任务")
        d.app_start("com.cat.readall")
        time.sleep(10)

        vc = VisualClicker(d)
        aw = WuKongAdWatcher(d)
        tm = TaskManager(d, app_name)
        rt = RevenueTracker()
        
        time.sleep(5)  # 等待界面加载完成
        def task_daily_checkin():
            if d(textContains="授权后体验完整功能").exists:
                click_by_xpath_text(d, xpaths='//*[@content-desc="关闭"]')
        tm.run_task_once("关闭授权提示", task_daily_checkin)
        # 点击去赚钱     
        if wait_exists(d(text="金币")):
            click_by_xpath_text(d, "金币")
            time.sleep(5)
            
# ------------    弹窗的处理   ----------------
            def task_daily_checkin():
                time.sleep(5)
                if d(textContains="立即报名").exists or d(textContains="继续打卡").exists:
                    print("识别【连续打开】弹窗...")
                    if click_by_xpath_text(d, "立即报名"):
                        click_by_xpath_text(d, "立即报名")
                        if click_by_xpath_text(d, "看视频得"):
                            aw.watch_ad()

                    elif click_by_xpath_text(d, "立即打卡"):
                        if click_by_xpath_text(d, "看视频得"):
                            aw.watch_ad()
            tm.run_task_once("分享7亿弹窗", task_daily_checkin)
            
            
            print("识别【连续签到】弹窗...")
            vc.set_targets(["额外再领", "看视频再领"])
            matched_text = vc.match_text()
            if matched_text in ["额外再领", "看视频再领"]:
                vc.find_and_click()
                time.sleep(2)
                aw.watch_ad() 
            
        if wait_exists(d(text="去提现")):
            print("⏳ 等待10秒让网页稳定....")
            time.sleep(5)
            print("✅ 加载完成，开始工作")
            
# ------------   日常任务处理   ----------------           
            if click_by_xpath_text(d, "领取金币"):
                if click_by_xpath_text(d, "看视频再领"):
                    aw.watch_ad()
        
            if click_by_xpath_text(d, "开宝箱得金币"):
                if click_by_xpath_text(d, "看视频额外"):
                    aw.watch_ad()
            
            time.sleep(5)
            print("识别【惊喜奖励】弹窗...")
            vc.set_targets(["看视频再领"])
            if vc.find_and_click():
                time.sleep(2)
                aw.watch_ad() 
                
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出      
    finally:
        import re
        click_by_xpath_text(d, "去提现")
        time.sleep(2)
        jinbi_text = d(className="com.lynx.tasm.behavior.ui.text.FlattenUIText", instance=3).get_text() or "0" 
        today_jinbi = float(re.sub(r'[^\d.]', '', jinbi_text))
        
        xianjin_text = d(className="com.lynx.tasm.behavior.ui.text.FlattenUIText", instance=4).get_text() or "0" 
        today_xianjin = float(re.sub(r'[^\d.]', '', xianjin_text))
        
        # 获取昨天的收入
        # 获取昨天值
        y_jinbi, y_xianjin = rt.get_yesterday_revenue("A3KUVB2428008483", "wukong")
        # 计算新增
        jinbi_value = today_jinbi - y_jinbi
        xianjin_value = today_xianjin - y_xianjin
        print(f"{app_name} 收益已记录: 金币={jinbi_value}, 现金={xianjin_value}")
        
        log(f"[{d.serial}] {app_name} 任务完成")
        d.app_stop("com.cat.readall")
        return xianjin_value, jinbi_value