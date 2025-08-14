import json
import os
from datetime import datetime, time
import time as t
import uiautomator2 as u2
from logger import log

class TaskManager:
    def __init__(self, device: u2.Device, app_package: str, state_file="task_state.json"):
        self.d = device
        self.app_package = app_package
        self.state_file = state_file
        self.state = self.load_state()

        # 在 TaskManager 里直接创建这些对象
        from Image_elements.visual_clicker import VisualClicker
        from ad_handler.douyin_handler import DouYinAdWatcher
        self.vc = VisualClicker(self.d)
        self.aw = DouYinAdWatcher(self.d)

    # ---------------- 状态管理 ----------------
    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def mark_done(self, task_name):
        today = datetime.today().strftime("%Y-%m-%d")
        self.state[task_name] = today
        self.save_state()

    def is_done(self, task_name):
        today = datetime.today().strftime("%Y-%m-%d")
        return self.state.get(task_name) == today

    # ---------------- 时间判断 ----------------
    @staticmethod
    def before_deadline(hour, minute=0):
        now = datetime.now().time()
        deadline = time(hour, minute)
        return now < deadline

    # ---------------- 任务执行示例 ----------------
    def run_task_once(self, task_name, task_func):
        """只执行一次的任务"""
        if not self.is_done(task_name):
            log(f"✅ 执行任务: {task_name}")
            task_func()
            self.mark_done(task_name)
        else:
            log(f"⚠️ 任务 {task_name} 已完成，跳过")

    def run_task_before(self, task_name, deadline_hour, task_func):
        """在指定时间前执行"""
        if self.before_deadline(deadline_hour):
            log(f"⏳ 执行时间任务: {task_name}")
            task_func()
        else:
            log(f"⚠️ 超过时间，不再执行 {task_name}")

