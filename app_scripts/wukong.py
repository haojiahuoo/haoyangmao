import time
import uiautomator2 as u2
from utils.device import d  # 从 utils 中引入设备连接对象
from utils.tools import *
from Image_elements.visual_clicker import VisualClicker
from ad_handler.wukong_handler import WuKongAdWatcher


def WuKongApp(app_startup_package):
    
    vc = VisualClicker(d)
    aw = WuKongAdWatcher(d)

    try:
        time.sleep(5)  # 等待界面加载完成
        # 点击去赚钱     
        if wait_exists(d(text="金币")):
            click_by_xpath_text(d, "金币", wait_gone=False)

            time.sleep(5)
            print("识别【惊喜奖励】弹窗...")
            vc.set_targets(["看视频再领"])
            if vc.find_and_click():
                time.sleep(2)
                aw.watch_ad() 
            
        if wait_exists(d(text="去提现")):
            print("⏳ 等待10秒让网页稳定....")
            time.sleep(10)
            print("✅ 加载完成，开始工作")
            
            if click_by_xpath_text(d, "领取金币", wait_gone=False):
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
        print(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出      
    finally:
        print("关闭悟空浏览器...")
        d.app_stop(app_startup_package)