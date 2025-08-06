import time
import uiautomator2 as u2
import time
from utils.device import d
from utils.tools import *
from Image_elements.visual_clicker import VisualClicker
from ad_handler.xigua_handler import XiGuaAdWatcher

def XiGuaApp(app_startup_package):
    try:
        vc = VisualClicker(d)
        aw = XiGuaAdWatcher(d)
        
        if wait_exists(d(textContains="我的")):
            d.xpath('//*[@resource-id="com.ss.android.article.video:id/dee"]').click()
        
        vc.target_texts = ["金币收益"]
        matched_text = vc.match_text()
        if matched_text == "金币收益":
            print("✅ 加载完成，开始工作")

            print("⏳ 开始识别[签到7天领金币]弹窗")
            vc.target_texts = ["立即签到+"]
            if vc.find_and_click():
                print("✅ 点击--立即签到+")
                vc.target_texts = ["看广告视频"]
                if vc.find_and_click():
                    print("✅ 点击--看广告视频")
                    aw.watch_ad()

            # 签到预约领金币
            vc.target_texts = ["明日0点", "24点前"]
            print("⏳ 开始识别", vc.target_texts)
            matched_text = vc.match_text()
            print("🧾 识别结果:", repr(matched_text))  # 调试用：查看实际识别结果
            if matched_text  == "明日0点":
                print("✅ 明天才能领取")
            elif matched_text  == "24点前":
                print("✅ 开始领取流程")
                vc.find_and_click()
                click_by_xpath_text(d, "一键领取")
                click_by_xpath_text(d, "开心收下")
                click_by_xpath_text(d, "立即预约领取")
                click_by_xpath_text(d, "提醒我来领")
                click_by_xpath_text(d, "领取奖励")
                aw.watch_ad()
                d.press("back")
            else:
                print("⚠️ 未匹配到任何目标文本")
        
            # 点击领宝箱
            print('⏳ 开始识别[宝箱任务]')
            vc.target_texts = ["点击领", "开宝箱"]
            matched_text = vc.match_text()
            print("🧾 识别结果:", repr(matched_text)) 
            if matched_text == "点击领" or "开宝箱":
                vc.find_and_click()
                time.sleep(2)
                
                vc.target_texts = ["看广告视频", "开心收下"]
                matched_text = vc.match_text()
                
                if matched_text in ["看广告视频", "开心收下"]:
                    vc.find_and_click()
                    if matched_text == "看广告视频":
                        aw.watch_ad()
                else:
                    print("⚠️ 未匹配到任何目标文本")
            else:
                print("⚠️ 未匹配到任何目标文本")
            
    finally:
        print("关闭西瓜...")
        d.app_stop(app_startup_package)

