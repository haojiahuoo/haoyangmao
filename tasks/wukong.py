import time
import uiautomator2 as u2
from utils.tools import *
from logger import log
from Image_elements.visual_clicker import VisualClicker
from ad_handler.wukong_handler import WuKongAdWatcher

def run(d: u2.Device):
    try:
        log(f"[{d.serial}] 启动 悟空浏览器")
        d.app_start("com.cat.readall")
        time.sleep(10)

        vc = VisualClicker(d)
        aw = WuKongAdWatcher(d)

        time.sleep(5)  # 等待界面加载完成
        # 点击去赚钱     
        if wait_exists(d(text="金币")):
            click_by_xpath_text(d, "金币")

            time.sleep(25)
            if d(textContains="授权后体验完整功能").exists:
                click_by_xpath_text(d, xpaths='//*[@content-desc="关闭"]')
            
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

            print("识别【连续签到】弹窗...")
            vc.set_targets(["额外再领"])
            if vc.find_and_click():
                time.sleep(2)
                aw.watch_ad() 
  
        if wait_exists(d(text="去提现")):
            print("⏳ 等待10秒让网页稳定....")
            time.sleep(10)
            print("✅ 加载完成，开始工作")
            
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
        log(f"[{d.serial}] 悟空浏览器 任务完成")
        d.app_start("com.cat.readall")