import threading
import random
import importlib
import time
from config import ACTIVE_DEVICES as DEVICES, TASKS, MAX_RETRY
from device import connect_device
from logger import log, set_default_device

task_locks = {task: threading.Lock() for task in TASKS}

def run_on_device(serial):
    d, device_id = connect_device(serial)
    set_default_device(d)  # 绑定设备，后续日志自动带设备ID

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
                task_module.run(d)
                break
            except Exception as e:
                log(f"任务 {task_name} 出错: {e}")
                if attempt == MAX_RETRY:
                    log(f"任务 {task_name} 达到最大重试次数，跳过")
            finally:
                lock.release()

    log("所有任务执行完毕 ✅")

if __name__ == "__main__":
    threads = []
    for serial in DEVICES:
        t = threading.Thread(target=run_on_device, args=(serial,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    log("🎯 全部设备任务执行完成！")
