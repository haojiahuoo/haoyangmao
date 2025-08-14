import uiautomator2 as u2
import datetime
import os
from collections import defaultdict
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import datetime

# ---------------- 收益统计类 ----------------
class RevenueTracker:
    def __init__(self, excel_dir="excel_reports", app_rates=None):
        self.excel_dir = excel_dir
        os.makedirs(self.excel_dir, exist_ok=True)
        self.app_rates = app_rates or {}
        self.today_data = defaultdict(lambda: {"jinbi":0, "xianjin":0})

    def get_excel_path(self, date_str):
        return os.path.join(self.excel_dir, f"{date_str}.xlsx")

    def add_revenue(self, app_name, device_name, jinbi=0, xianjin=0):
        key = (app_name, device_name)
        # 同一 APP + 设备覆盖，不同设备保留
        self.today_data[key]["jinbi"] = jinbi
        self.today_data[key]["xianjin"] = xianjin
        self.save_excel()  # 改成保存 Excel

    def save_excel(self):
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill
        import datetime

        wb = Workbook()
        ws = wb.active
        ws.title = "收益统计"

        headers = ["日期", "APP名", "设备名", "金币", "现金(元)", "总收益(元)"]
        ws.append(headers)
        for col in range(1, len(headers) + 1):
            ws.cell(row=1, column=col).font = Font(bold=True, size=12)

        date_str = datetime.date.today().isoformat()

        # 累计行样式
        total_fill = PatternFill(start_color="FFD966", end_color="FFD966", fill_type="solid")
        total_jinbi = sum(info["jinbi"] for info in self.today_data.values())
        total_xianjin = sum(info["xianjin"] for info in self.today_data.values())
        total_sum = sum(
            info["xianjin"] + info["jinbi"] / self.app_rates.get(app, 1)
            for (app, _), info in self.today_data.items()
        )

        ws.append([date_str, "累计", "", total_jinbi, total_xianjin, round(total_sum, 2)])
        ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=3)
        ws.cell(row=2, column=2).font = Font(bold=True, size=12)
        ws.cell(row=2, column=2).alignment = Alignment(horizontal="center")
        for cell in ws[2]:
            cell.fill = total_fill

        # 累计下方空行
        ws.append([])

        row_idx = 4
        apps = sorted(set(app for (app, _) in self.today_data.keys()))
        stat_fill = PatternFill(start_color="C9DAF8", end_color="C9DAF8", fill_type="solid")

        for app in apps:
            # 小统计行
            app_jinbi = sum(info["jinbi"] for (a, _), info in self.today_data.items() if a == app)
            app_xianjin = sum(info["xianjin"] for (a, _), info in self.today_data.items() if a == app)
            app_total = sum(
                info["xianjin"] + info["jinbi"] / self.app_rates.get(app, 1)
                for (a, _), info in self.today_data.items()
                if a == app
            )

            ws.append([date_str, app, "统计", app_jinbi, app_xianjin, round(app_total, 2)])
            ws.merge_cells(start_row=row_idx, start_column=3, end_row=row_idx, end_column=3)
            ws.cell(row=row_idx, column=3).font = Font(bold=True, size=12)
            ws.cell(row=row_idx, column=3).alignment = Alignment(horizontal="center")
            for cell in ws[row_idx]:
                cell.fill = stat_fill
            row_idx += 1

            # 设备明细
            devices = sorted(device for (a, device) in self.today_data.keys() if a == app)
            for device in devices:
                info = self.today_data[(app, device)]
                total = info["xianjin"] + info["jinbi"] / self.app_rates.get(app, 1)
                ws.append([date_str, app, device, info["jinbi"], info["xianjin"], round(total, 2)])
                row_idx += 1

            # APP 间空行
            ws.append([])
            row_idx += 1

        # 保存 Excel
        path = self.get_excel_path(date_str)
        wb.save(path)