import time, random
import uiautomator2 as u2
from utils.tools import *
from logger import bind_logger
from Image_elements.visual_clicker import VisualClicker
from ad_handler.UC_handler import UCAdWatcher
from utils.number import BracketNumberTool

def run(device_input):
    """统一入口处理设备输入"""
    # 确保设备对象正确初始化
    if isinstance(device_input, str):
        d = u2.connect(device_input)
        device_id = device_input
    else:
        d = device_input
        device_id = getattr(device_input, "serial", str(device_input))
    
    # 绑定日志器（确保传递字符串ID）
    log, log_error, log_debug = bind_logger(device_id)
    
    
    # 确保VisualClicker和UCAdWatcher接收设备对象
    vc = VisualClicker(d)
    aw = UCAdWatcher(d)
    
    log("启动 UC浏览器")
    d.app_start("com.ucmobile.lite")
    time.sleep(10)
    try:
        # 进入任务页面
        if click_by_xpath_text(d, xpaths="//*[@text='首页']/../../*[5]//android.widget.ImageView"):
            time.sleep(5)
            log_debug("识别恭喜获得元宝")
            vc.set_targets(["看视频再", "看激励视频", "周年福利","施肥可得"])
            matched_text = vc.match_text()
            if matched_text in ["看视频再", "看激励视频"]:
                vc.find_and_click()
                aw.watch_ad()
            elif matched_text == "周年福利":
                log_debug("识别周年福利")
                d.press("back")  # 返回上一页
            elif matched_text == ["施肥可得"]:
                time.sleep(random.uniform(1, 3))  # 等待1-3秒
                d.click(925, 783)  # 点击屏幕中心

            log_debug("识别是否进入任务页面...")
            vc.set_targets(["现金余额"])
            matched_text = vc.match_text()
            if matched_text == "现金余额":
                log("⏳ 等待10秒让网页稳定....")
                time.sleep(10)
                log("✅ 加载完成，开始工作")
                
            log_debug("识别开宝箱任务...")
            vc.set_targets(["开宝箱"])
            matched_text = vc.match_text()
            if matched_text == "开宝箱": 
                if vc.find_and_click():
                    vc.set_targets(["看视频再"])
                    matched_text = vc.match_text()
                    if matched_text == "看视频再":
                        vc.find_and_click()
                        aw.watch_ad()  
            
            vc.set_targets(["领元宝"])
            start_time = time.time()
            while time.time() - start_time < 1200:  # 最多等待60秒
                matched_text = vc.match_text(return_full_text=True)
                if matched_text and "领元宝" in matched_text:
                    if BracketNumberTool.compare(matched_text, "lt"):
                        log("✅ 还没满，执行点击")
                        if vc.find_and_click(target="领元宝"):
                            aw.watch_ad()
                    else:
                        log("⚠️ 已满或无法提取数字")
                        break
                else:
                    log("❌ 找不到按钮")
                    break
            log("✅ 时间太长了，别再看了...")
            
                    
    except Exception as e:
        log_error(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出      
    finally:
        log(f"[{d.serial}] UC浏览器 任务完成")
        d.app_start("com.ucmobile.lite")