import time
import uiautomator2 as u2
from utils.device import d  # 从 utils 中引入设备连接对象
from utils.tools import *
from Image_elements.visual_clicker import VisualClicker
from ad_handler.wukong_handler import WuKongAdWatcher


def WuKongApp(app_startup_package):
    
    vc = VisualClicker()
    aw = WuKongAdWatcher()

    try:
        time.sleep(5)  # 等待界面加载完成
        # 点击去赚钱     
        d(resourceId="com.cat.readall:id/bn7").click()
        print("点击去赚钱...")
        
        click_by_xpath_text(d, "开宝箱得金币")
        d.xpath("(//com.lynx.tasm.behavior.ui.LynxFlattenUI)[110]").click()
        
        vc.target_texts = ["额外再领"]
        if vc.find_and_click():
            print("✅ 点击--已连续签到")
            time.sleep(2)
            aw.watch_ad()
        
    finally:
        print("关闭悟空浏览器...")
        d.app_stop(app_startup_package)