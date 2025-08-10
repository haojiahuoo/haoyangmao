import subprocess
from logger import log

def get_connected_devices():
    """自动获取已连接的Android设备列表"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
        devices = [
            line.split('\t')[0]
            for line in result.stdout.splitlines()
            if '\tdevice' in line
        ]
        if devices:
            log(f"自动检测到设备: {devices}")
        else:
            log("未检测到连接设备")
        return devices
    except subprocess.CalledProcessError as e:
        log(f"adb命令执行失败: {e}", level="ERROR")
    except Exception as e:
        log(f"设备检测失败: {e}", level="ERROR")
    return []

# 配置策略（二选一）：
# 模式1. 手动指定设备（取消下面DEVICES的注释）
# 模式2. 自动检测设备（保持DEVICES = None）

DEVICES = None  # 设为None表示自动检测
# DEVICES = [  # 手动指定设备
#     "9a5dbfaf",
#     "emulator-5554",
# ]

ACTIVE_DEVICES = DEVICES if DEVICES is not None else get_connected_devices()

TASKS = [
    "UC",
    # "douyin",
    # "xigua",
    # "wukong",
    # "kuaishou",
    # "jinritoutiao"
]

MAX_RETRY = 3
