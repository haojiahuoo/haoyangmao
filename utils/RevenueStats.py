import uiautomator2 as u2
import os
import csv
from datetime import date
from collections import defaultdict

# ---------------- 收益统计类 ----------------
class RevenueStats:
    def __init__(self, daily_dir="reports/daily", monthly_dir="reports/monthly"):
        self.daily_dir = daily_dir
        self.monthly_dir = monthly_dir
        self.today_data = defaultdict(float)  # {app_name: revenue}
        os.makedirs(self.daily_dir, exist_ok=True)
        os.makedirs(self.monthly_dir, exist_ok=True)

    def add_app_revenue(self, app_name, amount):
        """添加某个APP当天收益"""
        self.today_data[app_name] += float(amount)

    def save_daily_report(self):
        """保存当天日报"""
        today_str = date.today().strftime("%Y-%m-%d")
        file_path = os.path.join(self.daily_dir, f"{today_str}.csv")
        total_revenue = sum(self.today_data.values())

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["App Name", "Revenue"])
            for app, rev in self.today_data.items():
                writer.writerow([app, rev])
            writer.writerow(["Total", total_revenue])

        print(f"✅ 每日收益报表已保存: {file_path}")
        self.today_data.clear()

    def save_monthly_report(self):
        """统计本月所有日报并生成月报"""
        today = date.today()
        month_str = today.strftime("%Y-%m")
        total_per_app = defaultdict(float)
        total_month = 0.0

        for fname in os.listdir(self.daily_dir):
            if fname.startswith(month_str):
                file_path = os.path.join(self.daily_dir, fname)
                with open(file_path, encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader)  # 跳过表头
                    for row in reader:
                        if row[0] == "Total":
                            total_month += float(row[1])
                        else:
                            total_per_app[row[0]] += float(row[1])

        month_file = os.path.join(self.monthly_dir, f"{month_str}.csv")
        with open(month_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["App Name", "Monthly Revenue"])
            for app, rev in total_per_app.items():
                writer.writerow([app, rev])
            writer.writerow(["Total", total_month])

        print(f"📅 月度收益报表已保存: {month_file}")

