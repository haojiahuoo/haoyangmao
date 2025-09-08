import sys
import os

# ===== 解决模块导入问题 =====
# 把项目根目录加入模块搜索路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from visual_clicker import VisualClicker
import uiautomator2 as u2
from flask import Flask, request, jsonify
from config import AndroidId
import subprocess
import re

    
app = Flask(__name__)

@app.route("/ocr_request", methods=["POST"])
def ocr_request():
    req_data = request.get_json()
    device_id = req_data.get("device")
    targets = req_data.get("targets", [])

    value = AndroidId.get(device_id)
    if value:
        print(f"识别出{device_id}的设备号是{value}")
    else:
        print("未找到设备")
    
    if not device_id or not targets:
        return jsonify({"success": False, "error": "缺少设备ID或目标文字"}), 400

    print(f"收到设备 {value} 的 OCR 请求，目标文字: {targets}")
    
    try:
        d = u2.connect(value)
    except Exception as e:
        print(f"连接设备 {value} 失败:", e)
        return jsonify({"success": False, "error": f"连接设备失败: {e}"}), 500

    vc = VisualClicker(d)
    vc.set_targets([targets])
    matched_text = vc.match_text()
    if matched_text == targets:
        cx_cy = vc.find_and_click(app_cx_cy=False)
        res = {
        "success": True,
        "result": [{"x": cx_cy[0], "y": cx_cy[1], "text": "目标文字"}]
        }
        print(f"找到文字: {targets},并获取坐标{cx_cy}")
    else:
        print(f"未识别到目标文字: {targets}")
        res = {"success": False, "result": []}

    return jsonify(res)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)


