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

# DEVICES = None  # 设为None表示自动检测
DEVICES = [  # 手动指定设备
    "9a5dbfaf",
    # "A3KUVB2428008483",
]

ACTIVE_DEVICES = DEVICES if DEVICES is not None else get_connected_devices()

TASKS = [
    "UC",
    "douyin",
    "xigua",
    "wukong",
    "kuaishou",
    "jinritoutiao",
    "fanqieyinyue",  # 番茄音乐
]

MAX_RETRY = 3

EXCHANGE_RATES = {
    "douyin": 10000,   # 抖音极速版：1000 金币 = 1 元
    "kuaishou": 10000, # 快手极速版：5000 金币 = 1 元
    "xigua": 33000,  # 今日头条极速版：3000 金币 = 1 元
    "jinritoutiao": 33000,  # 今日头条极速版：1000 金币 = 1 元
    "wukong": 33000,  # 猿辅导极速版：1000 金币 = 1 元    # 其他 APP...
    "UC": 33000,
    "fanqieyinyue": 33000,  # 番茄音乐：1000 金币 = 1 元
}