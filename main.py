import threading
import random
import importlib
import uiautomator2 as u2
import time
import datetime
from datetime import timedelta
from config import ACTIVE_DEVICES as DEVICES, TASKS, MAX_RETRY
from device import connect_device
from logger import *
from utils.revenuetracker import RevenueTracker  # 收益统计类
from config import EXCHANGE_RATES

# ---------------- 锁和收益统计 ----------------
task_locks = {task: threading.Lock() for task in TASKS}
stats = RevenueTracker(app_rates=EXCHANGE_RATES)  # 创建收益统计实例

def run_on_device(serial):
    d, device_id = connect_device(serial)
    set_default_device(d)
    log(f"设备启动任务，设备ID: {serial}")

    task_order = TASKS.copy()
    random.shuffle(task_order)

    for task_name in task_order:
        for attempt in range(1, MAX_RETRY + 1):
            lock = task_locks[task_name]
            acquired = lock.acquire(timeout=300)
            if not acquired:
                log(f"等待任务 {task_name} 锁超时，跳过")
                break

            try:
                log(f"第 {attempt} 次执行任务 {task_name}")
                # 先清理后台
                clear_recent_apps(d)
                task_module = importlib.import_module(f"tasks.{task_name}")
                if task_name == "kuaishou":
                    result = task_module.run(d, device_id)
                else:
                    result = task_module.run(d)

                # 如果任务返回 (jinbi, xianjin)
                if isinstance(result, tuple) and len(result) == 2:
                    jinbi, xianjin = result
                    stats.add_revenue(task_name, serial, jinbi, xianjin)
                    log(f"📊 {task_name} ({serial}): 金币 {jinbi} + 现金 {xianjin} = 总收益 {xianjin + jinbi/EXCHANGE_RATES.get(task_name,1):.2f} 元")

                # 如果任务只返回一个值（直接是元）
                elif isinstance(result, (int, float)):
                    stats.add_revenue(task_name, serial, 0, result)
                    log(f"📊 {task_name} ({serial}): 收益 +{result} 元")

                else:
                    log_error(f"⚠ 任务 {task_name} 返回值格式不正确: {result}")

                break
            except Exception as e:
                log_error(f"任务 {task_name} 出错: {e}")
                if attempt == MAX_RETRY:
                    log(f"任务 {task_name} 达到最大重试次数，跳过")
            finally:
                lock.release()

    log(f"设备 {serial} 所有任务执行完毕 ✅")
    log(f"🔥 当前总收益: {stats.get_today_total()} 元")

def clear_recent_apps(d: u2.Device):
    """
    清理后台运行的应用
    """
    try:
        d.press("home")
        time.sleep(1)
        d.press("recent")
        time.sleep(1.5)
        if d(description="最近无运行应用").exists:
            log("后台无运行应用")
            return
        clear_btns = [
            "com.oppo.launcher:id/btn_clear",
            "//*[@resource-id='com.hihonor.android.launcher:id/clearbox']",
            "com.miui.home:id/clearAnimView"
        ]

        found = False
        for i in clear_btns:
            clear_btn = d.xpath(i)
            if clear_btn.exists:
                clear_btn.click()
                time.sleep(2)
                found = True
                break

        if not found:
            d.press("back")
            log("找不到清理按钮")
            
    except Exception as e:
        log(f"清理后台异常: {e}")


# ---------------- 主循环 ----------------
if __name__ == "__main__":

    count = 0
    while True:
        now = datetime.datetime.now()

        # 到了 23:00 统计并退出
        if now.hour == 23 and now.minute == 0:
            log("🕚 到了23:00，开始执行收益统计任务...")
            clear_recent_apps()  # 清理后台
        
        else:
            count += 1
            threads = []
            for serial in DEVICES:
                t = threading.Thread(target=run_on_device, args=(serial,))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()
                
            log(f"🎯 第 {count} 次全部设备任务执行完成！")

        time.sleep(300)  # 控制循环频率
