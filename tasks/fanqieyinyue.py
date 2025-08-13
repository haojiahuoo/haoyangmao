import time
from utils.tools import *
import uiautomator2 as u2
from ad_handler.fanqieyinyue_handle import FanQieYinYueAdWatcher
from logger import log

def run(d: u2.Device):
    try:
        log(f"[{d.serial}] 启动 番茄音乐")
        d.app_start("com.xs.fm.lite")
        time.sleep(10)
        watcher = FanQieYinYueAdWatcher(d)


        d.xpath('//*[@resource-id="com.xs.fm.lite:id/ffv"]').click()
        print("点击暂停")
        click_by_xpath_text(d, "领现金")
        
        start = time.time()
        if wait_exists(d.xpath('//*[contains(@text, "新人礼加送现金")]')):
            print("🗨️ 发现-新人送现金-弹窗")
            click_by_xpath_text(d, "领取今日现金")
        print("耗时: ", time.time() - start) 
        
        start = time.time()
        # 判断是否存在抽奖弹窗
        if wait_exists(d.xpath('//*[contains(@text, "立即前往")]')):
            d(textContains="立即前往").click()
            print("🔄 点击立即前往")
            if wait_exists(d.xpath('//*[@text="抽奖"]')):
                d(text="抽奖").click()
                print("🔄 点击抽奖")
                if click_by_xpath_text(d, "看视频再抽一次"):
                        watcher.watch_ad()
                elif wait_exists(d.xpath('//*[contains(@text, "活动繁忙")]'), timeout=5):
                    d.press("back")
                    print("活动繁忙，点击后退...")
                    
        print("耗时: ", time.time() - start)
        
        start = time.time()
        if wait_exists(d(text="今日签到")):
            print("🗨️ 发现-今日签到-弹窗")
            click_by_xpath_text(d, "立即签到")
            if click_by_xpath_text(d, "看视频再领"):
                watcher.watch_ad()
        print("耗时: ", time.time() - start)
        
        start = time.time()
        if wait_exists(d(textContains="去赚更多")):
            pass   
        elif wait_exists(d(textContains="立即签到")):
            if click_by_xpath_text(d, "签到领现金"):
                click_by_xpath_text(d, ["继续赚金币", "明日再来"])
        print("耗时: ", time.time() - start)
        
        start = time.time()        
        if click_by_xpath_text(d, "开宝箱得金币"):
            if click_by_xpath_text(d, "看视频再得"):
                watcher.watch_ad()
        print("耗时: ", time.time() - start)        
    
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出      
    finally:
        log(f"[{d.serial}] 番茄音乐 任务完成")
        d.app_stop("com.xs.fm.lite")