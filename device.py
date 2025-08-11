import uiautomator2 as u2
from logger import log
import subprocess

def get_connected_devices():
    """获取当前所有已连接的设备序列号列表"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        return [
            line.split('\t')[0] 
            for line in result.stdout.splitlines() 
            if '\tdevice' in line
        ]
    except Exception as e:
        log(f"获取设备列表失败: {e}", level="ERROR")
        return []

def connect_device(serial):
    """确保始终返回 (device_object, device_id_string) 元组"""
    log(f"正在连接设备 {serial}")
    d = u2.connect(serial)
    
    try:
        # 获取规范的设备ID
        connected_id = d.serial if hasattr(d, "serial") else str(serial)
        log(f"✅ 设备 {connected_id} 已连接")
        return d, connected_id  # 确保第二个元素总是字符串
    except Exception as e:
        log(f"❌ 设备 {serial} 连接失败: {e}", level="ERROR")
        raise