import uiautomator2 as u2
import time
from utils.tools import *
from ad_handler.kuaishou_handler import KuaiShouAdWatcher
class PopupHandler:
    def __init__(self, device):
        """
        device: uiautomator2 设备对象
        ad_watcher: 负责看广告的对象（aw.watch_ad()）
        """
        self.d = device
        self.common_popups = [
            {"name": "获得优惠券", "element": "恭喜获得惊喜优惠券"},
            {"name": "今日签到可领", "element": "立即签到"},
            {"name": "添加到主屏幕", "element": "取消"},
            {"name": "看广告领领金币", "element": "看广告领"},
            {"name": "新用户必得", "element": "新用户必得"},
            {"name": "翻倍任务开启", "element": "翻倍任务开启"},
            {"name": "邀请好友", "element": "限时邀1位好友立得现金"},
            {"name": "邀请新用户", "element": "邀请2个新用户必得"},
            {"name": "连续打卡", "element": ["拿好礼 今日可打卡", "huge_sign_marketing_popup"]},
        ]

    def check_and_handle_popup(self, timeout=3.0):
        """
        检查并处理弹窗，直到没有可处理的弹窗
        返回 True 表示至少处理了一个弹窗
        """
        log("⏳ 检查并处理弹窗...")
        aw = KuaiShouAdWatcher(self.d) 
        handled_any = False
        while True:
            handled_this_round = False

            # 遍历常见弹窗列表
            for popup in self.common_popups:
                name = popup["name"]
                element = popup["element"]

                try:
                    # 特殊处理：看广告领领金币
                    if name == "看广告领领金币" and self.d(textContains="看广告领").exists(timeout=timeout):
                        log("🗨️ 发现-看广告领-弹窗")
                        click_by_xpath_text(self.d, "看广告领")
                        time.sleep(1)

                        # 点我领 iPhone
                        if click_by_xpath_text(self.d, "点我领iPhone"):
                            time.sleep(1)
                            if wait_exists(self.d.xpath('//*[contains(@elements, "去签到")]')):
                                click_by_xpath_text(self.d, "去签到")
                                click_by_xpath_text(self.d, "我知道了")
                                time.sleep(1)
                                self.d.press("back")

                        # 去看视频
                        if wait_exists(self.d.xpath('//*[contains(@elements, "去看视频")]')):
                            log("🗨️ 发现-去看视频-弹窗")
                            click_by_xpath_text(self.d, "去看视频")
                            time.sleep(1)
                            aw.watch_ad()
                            # 明日签到
                            if wait_exists(self.d.xpath('//*[contains(@elements, "明日签到可领")]')):
                                log("🗨️ 发现-去明日签-弹窗")
                                click_by_xpath_text(self.d, xpaths='//*[@elements="明日签到可领"]/../../../following-sibling::*[contains(@class, "android.widget.Image")]')

                        # 看视频最高
                        if self.d.xpath("//*[contains(@elements, '看视频最高')]").exists:
                            log("🗨️ 发现-看视频最高-弹窗")
                            click_by_xpath_text(self.d, xpaths="//*[contains(@elements, '看视频最高')]/../../preceding-sibling::*[1]//android.widget.Image")
                            time.sleep(1)

                        handled_this_round = True
                        handled_any = True
                        break
                    
                    # 特殊处理：优惠券弹窗
                    elif name == "获得优惠券" and wait_exists(self.d(textContains="恭喜获得惊喜优惠券")):
                        log(f"🗨️ 发现-{name}-弹窗")
                        time.sleep(2)
                        self.d.press("back") # 返回
                        handled_this_round = True
                        handled_any = True
                        break
                    
                    # 特殊处理：新用户必得
                    elif name == "新用户必得" and wait_exists(self.d(textContains="新用户必得")):
                        log("🗨️ 发现-新用户必得-弹窗")
                        time.sleep(2)
                        self.d.xpath("(//android.widget.ImageView)[2]").click()
                        log("🔙 返回上一层")
                        handled_this_round = True
                        handled_any = True
                        break

                    # 特殊处理：翻倍任务
                    elif name == "翻倍任务开启" and wait_exists(self.d(textContains="翻倍任务开启")):
                        log("🗨️ 发现-翻倍任务-弹窗")
                        click_by_xpath_text(self.d, "去看内容")
                        time.sleep(1)
                        aw.watch_ad()
                        handled_this_round = True
                        handled_any = True
                        break

                    # 特殊处理：邀请好友
                    elif name == "邀请好友" and wait_exists(self.d(textContains="限时邀1位好友立得现金")):
                        log("🗨️ 发现-邀请好友-弹窗")
                        self.d.press("back")
                        handled_this_round = True
                        handled_any = True
                        break

                    # 特殊处理：邀请新用户
                    elif name == "邀请新用户" and wait_exists(self.d(textContains="邀请2个新用户必得")):
                        log("🗨️ 发现-邀请新用户-弹窗")
                        element = self.d.xpath('//*[@elements="邀请2个新用户必得"]/../following-sibling::*[@class="android.widget.ImageView"]')
                        if element.exists:
                            element.click()
                            log("✅ 点击-关闭按钮")
                            time.sleep(1)
                        handled_this_round = True
                        handled_any = True
                        break

                    elif name == "连续打卡" and wait_exists(self.d(textContains="连续打卡")):
                        for e in element:  # element 是列表
                            if click_by_xpath_text(self.d, e):
                                log("🔄 点击连续打卡白拿手机")
                                time.sleep(5)
                                if self.d(textContains="与奖品擦肩而过").exists:
                                    click_by_xpath_text(self.d, "重新选择商品")
                                else:
                                    if click_by_xpath_text(self.d, "去签到"):
                                        time.sleep(2)
                                        self.d.press("back")
                                        # 回首页
                                        while True:
                                            if self.d(textContains="猜你喜欢").exists:
                                                log("✅ 全部任务已完成，返回首页")
                                                break
                                            else:
                                                self.d.press("back")
                                                time.sleep(2)
                                handled_this_round = True
                                handled_any = True
                                break


                    # 通用弹窗处理
                    elif isinstance(element, list):
                        for e in element:
                            if self.d(textContains=e).exists(timeout=timeout):
                                log(f"🗨️ 发现-{name}-弹窗")
                                click_by_xpath_text(self.d, e)
                                handled_this_round = True
                                handled_any = True
                                break
                    else:
                        if self.d(textContains=element).exists:
                            log(f"🗨️ 发现-{name}-弹窗")
                            click_by_xpath_text(self.d, element)
                            handled_this_round = True
                            handled_any = True
                            break

                except Exception as e:
                    log(f"❌ 处理弹窗失败 [{name}]: {str(e)}")
                    continue

            if not handled_this_round:
                break  # 本轮没有弹窗处理，退出循环

        if not handled_any:
            log("ℹ️ 没有发现弹窗需要处理")
        return handled_any

    # def monitor_popups(self, interval=2.0):
    #     """持续监控弹窗（后台线程使用）"""
    #     def run():
    #         while True:
    #             self.check_and_handle_popup()
    #             time.sleep(interval)
    #     t = threading.Thread(target=run, daemon=True)
    #     t.start()
    #     return t
