import time
import uiautomator2 as u2
import time
from utils.device import d
from utils.tools import *
from Image_elements.visual_clicker import VisualClicker
from ad_handler.douyin_handler import DouYinAdWatcher
from utils.smart_swipe import SmartSwipe

def DouYinApp(app_startup_package):
    try:
        vc = VisualClicker(d)
        aw = DouYinAdWatcher(d)
        ss = SmartSwipe(d)
        
        if wait_exists(d(textContains="首页")):
            d.xpath("//android.widget.TabHost/android.widget.FrameLayout[2]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.ImageView[2]").click()
            
        vc.target_texts = ["金币收益"]
        matched_text = vc.match_text()
        if matched_text == "金币收益":
            print("⏳ 等待20秒让网页稳定....")
            time.sleep(20)
            print("✅ 加载完成，开始工作")
            
            print("⏳ 开始识别[预约领金币]弹窗")
            vc.target_texts = ["预约领金币"]
            matched_text = vc.match_text()
            if matched_text  == "预约领金币":
                click_by_xpath_text(d, "立即预约领金币")
                print("✅ 开始领取流程")
                click_by_xpath_text(d, "一键领取", wait_gone=False)
                click_by_xpath_text(d, "开心收下")
                click_by_xpath_text(d, "立即预约领取", wait_gone=False)
                click_by_xpath_text(d, "提醒我来领")
                click_by_xpath_text(d, "领取奖励")
                aw.watch_ad()
                d.press("back")
            else:
                print("⚠️ 未匹配到任何目标文本")
            
            
            print("识别已连续签到")
            vc.target_texts = ["已连续签到"]
            matched_text = vc.match_text()
            if matched_text == "已连续签到":
                vc.find_and_click()
                vc.target_texts = ["签到领"]
                if vc.find_and_click():
                    print("✅ 点击--签到领")
                    time.sleep(2)
                    vc.target_texts = ["看广告"]
                    if vc.find_and_click():
                        print("✅ 点击--看广告")
                        aw.watch_ad()
            
            print("⏳ 开始识别[新人签到领大额金币]弹窗")
            vc.target_texts = ["立即签到+"]
            if vc.find_and_click():
                print("✅ 点击--立即签到+")
                time.sleep(1)
                print("✅ 识别明天再来")
                vc.target_texts = ["明天再来"]
                if vc.find_and_click():
                    print("✅ 点击--明天再来")
            
            
            print("⏳ 开始识别[新人签到领金币]")
            vc.target_texts = ["新人签到领金币"]
            if vc.find_and_click():
                time.sleep(1)
                print("✅ 识别明天再来")
                vc.target_texts = ["明天再来"]
                if vc.find_and_click():
                    print("✅ 点击--明天再来")
            

            pos = vc.find_text_position("日常任务")
            if pos:
                x, y = pos
                # 拖动到顶部（比如 y=100）
                d.swipe(x, y, x, 600, 0.3)
            
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
                click_by_xpath_text(d, "一键领取", wait_gone=False)
                click_by_xpath_text(d, "开心收下")
                click_by_xpath_text(d, "立即预约领取", wait_gone=False)
                click_by_xpath_text(d, "提醒我来领")
                click_by_xpath_text(d, "领取奖励")
                aw.watch_ad()
                d.press("back")
            else:
                print("⚠️ 未匹配到任何目标文本")

            # 打卡领五粮液
            print('⏳ 开始识别["今日已打卡", "今日待打卡"]')
            vc.target_texts = ["今日已打卡", "今日待打卡"]
            matched_text = vc.match_text()
            if matched_text == "今日已打卡":
                print("✅ 明天再来打卡")
            elif matched_text == "今日待打卡":
                vc.find_and_click()
                click_by_xpath_text(d, "点击打卡")
                time.sleep(5)
                d.press("back")
            else:
                print("⚠️ 未匹配到任何目标文本")
            
            # 天天领金币
            print('⏳ 开始识别["明日签到立即", "今日签到立即"]')
            vc.target_texts = ["明日签到立即", "今日签到立即"]
            matched_text = vc.match_text()
            if matched_text == "明日签到立即":
                print("⏳ 明天才能领取")
            elif matched_text == "今日签到立即":
                vc.find_and_click()
                vc.target_texts = ["今日可领"]
                vc.find_and_click()
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
                if matched_text == "看广告视频":
                    vc.find_and_click()
                    aw.watch_ad()
                elif matched_text == "开心收下":
                    vc.find_and_click()
                    d.press("back")
                else:
                    d.click(100,100)
            else:
                print("⚠️ 未匹配到任何目标文本")
            
    finally:
        print("关闭抖音...")
        d.app_stop(app_startup_package)

