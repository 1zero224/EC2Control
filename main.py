"""
AWS EC2 实例管理 GUI 应用
应用程序入口

使用方法:
    python main.py
"""

import sys
from pathlib import Path

# 将 src 目录添加到模块搜索路径
sys.path.insert(0, str(Path(__file__).parent))

import flet as ft

from src.ui.app import EC2ManagerApp


def main(page: ft.Page):
    """应用主入口"""
    EC2ManagerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
