import uiautomator2 as u2
import time, threading
from utils.tools import *
from utils.popuphandler import PopupHandler
from app_scripts.kuaishou import KuaiShouApp
from app_scripts.douyin import DouYinApp
from app_scripts.fanqieyinyue import FanQeiYinYueApp
from app_scripts.wukong import WuKongApp
from app_scripts.jinritoutiao import JinRiTouTiaoApp
# # try:
# d = u2.connect("9a5dbfaf")
# # except:
d = u2.connect("A3KUVB2428008483")

handler = PopupHandler(d)

# 配置点击前延时0.5s，点击后延时1s
d.settings['operation_delay'] = (.5, 1)

# 启动后台线程运行监控
monitor_thread = threading.Thread(
    target=handler.monitor_popups,
    daemon=True  # 设置为守护线程（主程序退出时自动结束）
)
# monitor_thread.start()


def Start_working(apps):
    """启动所有APP并逐个处理"""
    
    # 第一步：依次启动所有App，预热准备
    for name, app_startup_package in apps:
        print(f"预启动{name}APP...")
        d.app_start(app_startup_package)
        time.sleep(5)  # 给每个 App 一点时间进入后台加载
        if name == "快手极速版":
            click_by_xpath_text(d, "去赚钱")
            time.sleep(10)
        elif name == "抖音极速版":
            if wait_exists(d(textContains="消息")):
                print("✅ 加载完成，开始工作")
                d.xpath('//*[@resource-id="com.ss.android.ugc.aweme.lite:id/d7y"]').click()
                time.sleep(10)
    # 第二步：依次回到每个App进行操作
    for name, app_startup_package in apps:
        print(f"正式启动{name}APP并操作...")
        d.app_start(app_startup_package)  # 切换回此 App 前台
        time.sleep(5)  # 等待界面加载完成
        
        if name == "快手极速版":
            KuaiShouApp(app_startup_package)
        elif name == "抖音极速版":
            DouYinApp(app_startup_package)
        elif name == "今日头条":
            JinRiTouTiaoApp(app_startup_package)
        # elif name == "西瓜视频":
        #     XiGuaApp(app_startup_package)  # 如果后面要加，记得实现这个函数
        # elif name == "火山小视频":
        #     HuoShanApp(app_startup_package)
        # elif name == "番茄畅听音乐":
        #     FanQeiYinYueApp(app_startup_package)    
        # elif name == "悟空浏览器":
        #     WuKongApp(app_startup_package)

# App 列表
apps = [
("快手极速版", "com.kuaishou.nebula"),
("抖音极速版", "com.ss.android.ugc.aweme.lite"),
("今日头条", "com.ss.android.article.lite"),
# ("番茄畅听音乐", "com.xs.fm.lite"),
# ("悟空浏览器", "com.cat.readall"),

]

Start_working(apps)
