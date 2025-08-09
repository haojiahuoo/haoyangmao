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
        
        try:
            target = d.xpath('//android.widget.RelativeLayout[3]//android.widget.ImageView[contains(@resource-id, "com.ss.android.article.video:id")]')
            target.click(timeout=5)
        except Exception as e:
            print(f"⚠️ 点击失败: {e}")
        
        vc.set_targets(["金币收益"])
        matched_text = vc.match_text()
        if matched_text == "金币收益":
            print("⏳ 等待20秒让网页稳定....")
            time.sleep(20)
            print("✅ 加载完成，开始工作")
            
            
            print("⏳ 开始识别[签到7天领金币]弹窗")
            vc.set_targets(["立即签到+"])
            if vc.find_and_click():
                print("✅ 点击--立即签到+")
                vc.set_targets(["看广告视频"])
                if vc.find_and_click():
                    print("✅ 点击--看广告视频")
                    aw.watch_ad()
            
            print("⏳ 开始识别[开宝箱奖励]弹窗")
            vc.set_targets(["看广告视频"])
            if vc.find_and_click():
                print("✅ 点击--看广告视频")
                aw.watch_ad()
            
                    
            print("⏳ 开始识别[预约领金币]弹窗")
            vc.set_targets(["预约领金币"])
            matched_text = vc.match_text()
            if matched_text  == "预约领金币":
                if click_by_xpath_text(d, "立即领取"):
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
                
                
            vc.set_targets(["日常任务"])
            pos =  vc.find_and_click()
            if pos:
                x, y = pos
                # 拖动到顶部（比如 y=100）
                d.swipe(x, y, x, 600, 0.3)

            # 签到预约领金币
            print("⏳ 开始识别[预约领金币]")
            vc.set_targets(["今日预约", "24点前", "明日0点", "明日11点"])
            matched_text = vc.match_text()
            print("🧾 识别结果:", repr(matched_text))  # 调试用：查看实际识别结果
            if matched_text in ["明日0点", "明日11点"]:
                print("✅ 明天再来！")
            elif matched_text in ["今日预约", "24点前"]:
                print("✅ 开始领取流程")
                vc.find_and_click()
                click_by_xpath_text(d, ["立即预约领取", "一键领取"], wait_gone=False)
                click_by_xpath_text(d, "开心收下")
                click_by_xpath_text(d, "立即预约领取", wait_gone=False)
                click_by_xpath_text(d, "提醒我来领")
                click_by_xpath_text(d, "领取奖励")
                aw.watch_ad()
                d.press("back")
            else:
                print("⚠️ 未匹配到任何目标文本")
        
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
        print(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出
    finally:
        print("🔚 关闭西瓜...")
        d.app_stop(app_startup_package)

