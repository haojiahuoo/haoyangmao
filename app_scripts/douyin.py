import time
import uiautomator2 as u2
import time
from utils.device import d
from utils.tools import *
from Image_elements.visual_clicker import VisualClicker
from ad_handler.douyin_handler import DouYinAdWatcher

def DouYinApp(app_startup_package):
    try:
        vc = VisualClicker(d)
        aw = DouYinAdWatcher(d)
        
        time.sleep(10)
        print("🔍 开始识别[已连续签到]")
        vc.target_texts = ["已连续签到"]
        if vc.find_and_click():
            print("✅ 点击--已连续签到")
            time.sleep(2)
            vc.target_texts = ["签到领"]
            print("识别签到领")
            if vc.find_and_click():
                print("✅ 点击--签到领")
            time.sleep(2)
            vc.target_texts = ["看广告"]
            if vc.find_and_click():
                print("✅ 点击--看广告")
                aw.watch_ad()
        
        print("🔍 开始识别[新人签到领大额金币]弹窗")
        vc.target_texts = ["立即签到+"]
        if vc.find_and_click():
            print("✅ 点击--立即签到+")
        
        
        print("🔍 开始识别[新人签到领金币]")
        vc.target_texts = ["新人签到领金币"]
        if vc.find_and_click():
            time.sleep(1)
            print("🔍 识别明天再来")
            vc.target_texts = ["明天再来"]
            if vc.find_and_click():
                print("✅ 点击--明天再来")
        
        
        # 签到预约领金币
        vc.target_texts = ["明日0点", "24点前"]
        print("🔍 开始识别", vc.target_texts)
        matched_text = vc.match_text()
        print("🧾 识别结果:", repr(matched_text))  # 调试用：查看实际识别结果
        if matched_text  == "明日0点":
            print("⏳ 明天才能领取")
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

        # 打卡领五粮液
        print('🔍 开始识别["今日已打卡", "今日待打卡"]')
        vc.target_texts = ["今日已打卡", "今日待打卡"]
        matched_text = vc.match_text()
        if matched_text == "今日已打卡":
            print("⏳ 明天再来打卡")
        elif matched_text == "今日待打卡":
            vc.find_and_click()
            click_by_xpath_text(d, "点击打卡")
            time.sleep(2)
            d.press("back")
        else:
            print("⚠️ 未匹配到任何目标文本")
        
        # # 天天领金币
        # print('🔍 开始识别["明日签到立即", "今日签到立即"]')
        # vc = VisualClicker(d, target_texts=["明日签到立即", "今日签到立即"])
        # matched_text = vc.match_text()
        # if matched_text == "明日签到立即":
        #     print("⏳ 明天才能领取")
        # elif matched_text == "今日签到立即":
        #     vc.find_and_click()
        # else:
        #     print("⚠️ 未匹配到任何目标文本")
        
        # 点击领宝箱
        vc.target_texts = ["点击领", "开宝箱"]
        if vc.find_and_click():
            print("✅ 点击--已领金币")
            time.sleep(2)
            
            vc.target_texts = ["看广告", "开心收下"]
            matched_text = vc.match_text()
            
            if matched_text in ["看广告", "开心收下"]:
                vc.find_and_click()
                if matched_text == "看广告":
                    aw.watch_ad()
            else:
                print("⚠️ 未匹配到任何目标文本")
        else:
            print("⚠️ 未匹配到任何目标文本")
        
    finally:
        print("关闭抖音...")
        d.app_stop(app_startup_package)

