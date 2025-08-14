import threading
import random
import importlib
import uiautomator2 as u2
import time, datetime
from datetime import timedelta
from config import ACTIVE_DEVICES as DEVICES, TASKS, MAX_RETRY
from device import connect_device
from logger import log, set_default_device
from utils.revenuestats import *

# ---------------- 原 run_on_device 逻辑 ----------------
task_locks = {task: threading.Lock() for task in TASKS}
stats = RevenueStats()

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
                task_module = importlib.import_module(f"tasks.{task_name}")
                result = task_module.run(d)  # 假设返回收益数
                if isinstance(result, (int, float)):
                    stats.add_app_revenue(task_name, result)
                break
            except Exception as e:
                log(f"任务 {task_name} 出错: {e}")
                if attempt == MAX_RETRY:
                    log(f"任务 {task_name} 达到最大重试次数，跳过")
            finally:
                lock.release()

    log("所有任务执行完毕 ✅")

def clear_recent_apps(d: u2.Device):
    try:
        # 打开最近任务
        d.press("recent")  # 比用xpath更稳
        time.sleep(1.5)
        
        clear_btns = [
            "com.oppo.launcher:id/btn_clear",
            "//*[@resource-id='com.hihonor.android.launcher:id/clearbox']",
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
            print("找不到清理按钮")

        # 返回桌面
        d.press("home")
        time.sleep(1)
    except Exception as e:
        print(f"清理后台异常: {e}")

# ---------------- 主循环 ----------------
if __name__ == "__main__":
    count = 0

    while True:
        now = datetime.datetime.now()

        # 如果到 23:00 执行统计并退出
        if now.hour == 23 and now.minute == 0:
            log("🕚 到了23:00，开始执行收益统计任务...")

            # 最后执行一次设备任务
            threads = []
            for serial in DEVICES:
                t = threading.Thread(target=run_on_device, args=(serial,))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            # 保存日报
            stats.save_daily_report(d)

            # 如果是月底，保存月报
            tomorrow = now + timedelta(days=1)
            if tomorrow.month != now.month:
                stats.save_monthly_report()

            log("📌 收益统计完成，退出程序")
            break

        # 白天正常任务
        if now.hour < 23 or (now.hour == 23 and now.minute < 0):
            count += 1
            threads = []
            for serial in DEVICES:
                t = threading.Thread(target=run_on_device, args=(serial,))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            # 多设备分别清理后台
            for serial in DEVICES:
                d, _ = connect_device(serial)
                clear_recent_apps(d)

            log(f"🎯 第 {count} 次全部设备任务执行完成！")


        time.sleep(5)  # 控制循环频率
