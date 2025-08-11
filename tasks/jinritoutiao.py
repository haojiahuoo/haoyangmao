import time
from utils.tools import *
import uiautomator2 as u2
from ad_handler.jinritoutiao_handler import JinRiTouTiaoAdWatcher
from utils.smart_swipe import SmartSwipe
from Image_elements.visual_clicker import VisualClicker
import random
from logger import log

def run(d: u2.Device):
    try:
<<<<<<< HEAD:app_scripts/jinritoutiao.py
=======
        log(f"[{d.serial}] 启动 今日头条")
        d.app_start("com.ss.android.article.lite")
        time.sleep(10)
        aw = JinRiTouTiaoAdWatcher(d)
        ss = SmartSwipe(d)
        vc = VisualClicker(d)
    
>>>>>>> 0d02bcbdfe068b997095f0cb1ce382457d2e7bd0:tasks/jinritoutiao.py
        if wait_exists(d(text="首页")):
            d.xpath('//*[@resource-id="com.ss.android.article.lite:id/a1q"]').click()
        time.sleep(10)
        
        print("⏳ 开始识别[恭喜获得]弹窗")
        vc.target_texts = ["看视频"]
        if vc.find_and_click():
            print("✅ 点击--看视频")
            aw.watch_ad()

        if wait_exists(d(description="翻倍领取")):
            print("🗨️ 发现-今日签到-弹窗")
            d.xpath('//*[contains(@content-desc, "翻倍领取")]').click()
            aw.watch_ad()    
            d.xpath('//*[contains(@content-desc, "好的")]').click()
            print("⏳ 开始识别[恭喜获得]弹窗")
<<<<<<< HEAD:app_scripts/jinritoutiao.py
            vc.target_texts = ["看视频"]
=======
            vc.set_targets["看视频"]
>>>>>>> 0d02bcbdfe068b997095f0cb1ce382457d2e7bd0:tasks/jinritoutiao.py
            if vc.find_and_click():
                print("✅ 点击--看视频")
                aw.watch_ad()

        if wait_exists(d(textContains="恭喜被新人")):
            print("🗨️ 发现-新人红包-弹窗")
            d.xpath("(//com.lynx.tasm.behavior.ui.view.UIView)[5]").click()
            time.sleep(1)
            
        if wait_exists(d(textContains="7天签到最高")):
            print("🗨️ 发现-签到红包-弹窗")
            click_by_xpath_text(d, "签到最高")
            time.sleep(1)    
            click_by_xpath_text(d, "去赚更多")
    
        if wait_exists(d(textContains="恭喜获得惊喜奖励")):
            print("🗨️ 发现-惊喜奖励-弹窗")
            click_by_xpath_text(d, "看视频")
            time.sleep(1)    
            aw.watch_ad()
            
        if wait_exists(d(textContains="寻宝得现金")):
            print("🗨️ 发现-签到-弹窗")
            click_by_xpath_text(d, "去寻宝")
            time.sleep(1)
            while True:
                time.sleep(3)
                d.xpath('(//com.lynx.tasm.behavior.ui.view.UIView)[20]').click()
                if wait_exists(d(textContains="糟糕！遇到海盗了")):
                    print("🗨️ 发现-海盗-弹窗")
                    click_by_xpath_text(d, "看广告击败海盗")
                    time.sleep(1)
                    aw.watch_ad()
                    d.xpath('(//com.lynx.tasm.behavior.ui.view.UIView)[25]').click()
        
        if wait_exists(d(textContains="开宝箱得金币")):
            print("🗨️ 发现-宝箱-弹窗")
            click_by_xpath_text(d, "开宝箱")
            time.sleep(1)
            d.xpath('(//android.view.ViewGroup)[11]').click()
            aw.watch_ad()
        
        if click_by_xpath_text(d, "+100"):
            time.sleep(2)
            if wait_exists(d(textContains="回到顶部")):
                while True:
                    ss.smart_swipe(direction="up")
                    vc.set_targets(["看视频再得"])
                    matched_text = vc.match_text()
                    if matched_text == "看视频再得":
                        vc.find_and_click()
                        aw.watch_ad()
                        break
                    
                    wait_time = random.uniform(0.5, 1.5) 
                    time.sleep(wait_time)
        
        if click_by_xpath_text(d, "逛街最多再领"):
            if wait_exists(d(textContains="恭喜获得惊喜奖励")):
                print("🗨️ 发现-惊喜奖励-弹窗")
                click_by_xpath_text(d, "看视频")
                time.sleep(1)    
                aw.watch_ad()
            else:
                while True:
                    ss.smart_swipe(direction="up")
                    vc.set_targets(["看视频再得"])
                    matched_text = vc.match_text()
                    if matched_text == "看视频再得":
                        vc.find_and_click()
                        aw.watch_ad()
                        break
                    
                    wait_time = random.uniform(0.5, 1.5) 
                    time.sleep(wait_time)
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出
    finally:
<<<<<<< HEAD:app_scripts/jinritoutiao.py
        print("关闭今天头条.....")
        d.app_stop(app_startup_package)
=======
        log(f"[{d.serial}] 今日头条 任务完成")
        d.app_stop("com.ss.android.article.lite")
>>>>>>> 0d02bcbdfe068b997095f0cb1ce382457d2e7bd0:tasks/jinritoutiao.py
