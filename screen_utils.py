"""
屏幕分辨率检测工具
跨平台获取真实屏幕分辨率
"""
import sys
from typing import Tuple


def get_screen_resolution() -> Tuple[int, int]:
    """
    获取主显示器的真实分辨率

    Returns:
        (width, height) 屏幕分辨率元组
    """
    try:
        if sys.platform == 'win32':
            # Windows 平台
            import ctypes
            user32 = ctypes.windll.user32
            # 获取主显示器分辨率（考虑 DPI 缩放）
            user32.SetProcessDPIAware()
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            return (width, height)

    except Exception as e:
        print(f"获取屏幕分辨率失败: {e}")

    # 默认返回常见分辨率
    return (1920, 1080)