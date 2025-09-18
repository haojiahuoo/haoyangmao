import time
import uiautomator2 as u2
from utils.tools import *
from ad_handler.kuaishou_handler import KuaiShouAdWatcher
from popup.kuaishou_popup import PopupHandler
from utils.smart_swipe import *
from logger import log

def run(d: u2.Device):
    try:
        app_name = "快手极速版"
        log(f"[{d.serial}] 启动 {app_name} 任务")
        d.app_start("com.kuaishou.nebula")
        time.sleep(10)

        aw = KuaiShouAdWatcher(d)
        ss = SmartSwipe(d) 
        handler = PopupHandler(d)
        
        if wait_exists(d(textContains="朋友推荐")):
            log("🗨️ 发现-朋友推荐-弹窗")
            d.xpath('//*[@text="朋友推荐"]/following-sibling::*[contains(@resource-id, "close_btn")]').click()
            time.sleep(1)
            
        click_by_xpath_text(d, "去赚钱")
        time.sleep(random.uniform(8, 10))
        if wait_exists(d(textContains="猜你喜欢")):
            log("⏳ 让网页稳定几秒....")
            time.sleep(random.uniform(3, 5))
            log("✅ 加载完成，开始工作")
        
            # 处理可能出现的弹窗
            handler.check_and_handle_popup(timeout=5)   
    #---------------- 每日执行一次的任务 ----------------
            

            log("⏳ 识别-看广告得金币")
            if wait_exists(d(textContains="冷却中")):
                pass
            else:
                if click_by_xpath_text(d, "看广告得金币"):
                    aw.watch_ad()
                
            log("⏳ 识别-宝箱任务")
            if click_by_xpath_text(d, "点可领"):
                aw.watch_ad() 
                
            log("⏳ 开始拖动--猜你喜欢")
            el = d(text="猜你喜欢")
            ss.smart_drag(d, origin=el, target=(650, 0.3)) 
            
            log("⏳ 点击看视频赚金币")  
            if click_by_xpath_text(d, "看视频赚金币"):
                a = time.time()
                while True:
                    ss.smart_swipe()
                    if time.time() - a > 2400:
                        break
                    time.sleep(random.uniform(8, 18))
            
                
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出
    finally:
        import re
        click_by_xpath_text(d, "我的金币")
        time.sleep(2)
        jinbi_text = d(className="android.widget.TextView", instance=3).get_text() or "0" 
        jinbi_value = float(re.sub(r'[^\d.]', '', jinbi_text))
        
        xianjin_text = d(className="android.widget.TextView", instance=5).get_text() or "0"
        num_str = str(xianjin_text)  # 转换为字符
        xianjin_value = float(num_str[0] + "." + num_str.split(".")[1][0])
        log(f"{app_name} 收益已记录: 金币={jinbi_value}, 现金={xianjin_value}")
            
        log(f"[{d.serial}] {app_name} 任务完成")
        d.app_stop("com.kuaishou.nebula")
        return jinbi_value, xianjin_value
