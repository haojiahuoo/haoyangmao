import time
import uiautomator2 as u2
from utils.tools import *
from ad_handler.kuaishou_handler import KuaiShouAdWatcher
from logger import log

def run(d: u2.Device):
    try:
        log(f"[{d.serial}] 启动 快手极速版")
        d.app_start("com.kuaishou.nebula")
        time.sleep(10)

        aw = KuaiShouAdWatcher(d)
        
        click_by_xpath_text(d, "去赚钱")
        if click_by_xpath_text(d, "猜你喜欢"):
            print("⏳ 等待20秒让网页稳定....")
            time.sleep(20)
            print("✅ 加载完成，开始工作")
            
            if wait_exists(d(textContains="朋友推荐")):
                print("🗨️ 发现-朋友推荐-弹窗")
                d.xpath('//*[@text="朋友推荐"]/following-sibling::*[contains(@resource-id, "close_btn")]').click()
                time.sleep(1)

            if wait_exists(d(textContains="今日签到可领")):
                print("🗨️ 发现-签到-弹窗")
                click_by_xpath_text(d, "立即签到")
                time.sleep(1)                                   
                
                if click_by_xpath_text(d, "点我领iPhone"):
                    time.sleep(1)
                    if wait_exists(d.xpath('//*[contains(@text, "去签到")]')):
                        click_by_xpath_text(d, "去签到")
                        click_by_xpath_text(d, "我知道了")
                        time.sleep(1)
                        d.press("back")
                    
                if wait_exists(d.xpath('//*[contains(@text, "去看视频")]')):
                    print("🗨️ 发现-去看视频-弹窗")
                    click_by_xpath_text(d, "去看视频")
                    time.sleep(1)
                    aw.watch_ad()
                    if wait_exists(d.xpath('//*[contains(@text, "明日签到可领")]')):
                        print("🗨️ 发现-去明日签-弹窗")
                        click_by_xpath_text(d, xpaths = '//*[@text="明日签到可领"]/../../../following-sibling::*[contains(@class, "android.widget.Image")]')
                        
                if d.xpath("//*[contains(@text, '看视频最高')]").exists:
                    print("🗨️ 发现-看视频最高-弹窗")
                    click_by_xpath_text(d, xpaths="//*[contains(@text, '看视频最高')]/../../preceding-sibling::*[1]//android.widget.Image")
                    time.sleep(1)
                       
                    
            if wait_exists(d(textContains="新用户必得")):
                print("🗨️ 发现-新用户必得-弹窗")
                time.sleep(2)
                d.xpath("(//android.widget.ImageView)[2]").click()
                print("🔙 返回上一层")

            if wait_exists(d(textContains="翻倍任务开启")):
                print("🗨️ 发现-翻倍任务-弹窗")
                click_by_xpath_text(d, "去看内容")
                time.sleep(1)
                aw.watch_ad()
                
            if wait_exists(d(textContains="限时邀1位好友立得现金")):
                print("🗨️ 发现-邀请好友-弹窗")
                d.press("back")
                print("🔙 返回上一层")
                
            if wait_exists(d(textContains="邀请2个新用户必得")):
                print("🗨️ 发现-邀请新用户-弹窗")
                # 获取目标ImageView元素（叔叔节点）
                element = d.xpath('//*[@text="邀请2个新用户必得"]/../following-sibling::*[@class="android.widget.ImageView"]')
                if element.exists:
                    element.click()
                    print("✅ 点击-关闭按钮")
                    time.sleep(1)
                    
            if click_by_xpath_text(d, ["拿好礼 今日可打卡", "huge_sign_marketing_popup"]):
                print("🔄 点击连续打卡白拿手机")
                time.sleep(5)
                if click_by_xpath_text(d, "去签到"):
                    time.sleep(2)
                    d.press("back")
                    while True:
                        if d(textContains="猜你喜欢").exists:
                            print("✅ 全部任务已完成，返回首页")
                            break
                        else:   
                            d.press("back")
                            time.sleep(2)
                            
            print("⏳ 识别-看广告得金币")
            if wait_exists(d(textContains="冷却中")):
                pass
            else:
                click_by_xpath_text(d, "看广告得金币")
                aw.watch_ad()
                
            print("⏳ 识别-宝箱任务")
            if click_by_xpath_text(d, "点可领"):
                aw.watch_ad() 
    except Exception as e:
        log(f"❌ 出错退出：{e}")
        raise  # 如果需要保留异常，可以重新抛出
    finally:
        log(f"[{d.serial}] 快手极速版 任务完成")
        d.app_stop("com.kuaishou.nebula")
