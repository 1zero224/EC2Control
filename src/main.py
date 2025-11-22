"""
AWS EC2 实例管理 GUI 应用
应用程序入口
"""

import flet as ft

from src.ui.app import EC2ManagerApp


def main(page: ft.Page):
    """应用主入口"""
    EC2ManagerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
