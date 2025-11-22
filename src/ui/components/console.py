"""
控制台日志面板组件
"""
import flet as ft
from flet import Icons
from datetime import datetime

from src.config.constants import CONSOLE_MAX_LINES


class ConsolePanel:
    """控制台日志面板组件"""

    def __init__(self, font, t_func):
        """
        初始化控制台面板

        Args:
            font: FontScale 实例
            t_func: 翻译函数
        """
        self.font = font
        self.t = t_func
        self._build()

    def _build(self):
        """构建控制台UI"""
        # 控制台输出列表
        self.output = ft.ListView(
            spacing=2,
            padding=10,
            auto_scroll=True,
        )

        console_height = int(130 * self.font.scale)
        self.container = ft.Container(
            content=self.output,
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.BLACK),
            border_radius=6,
            padding=0,
            height=console_height,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
        )

        self.header_text = ft.Text(
            self.t("console_output"),
            size=self.font.small,
            weight=ft.FontWeight.W_400,
            color=ft.Colors.WHITE70,
            font_family="YaHei"
        )

        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(Icons.TERMINAL, size=self.font.icon_small, color=ft.Colors.GREEN_400),
                    self.header_text,
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.BLACK),
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=ft.border_radius.only(top_left=6, top_right=6),
        )

    def get_control(self) -> ft.Column:
        """获取完整的控制台控件"""
        return ft.Column([self.header, self.container], spacing=0)

    def log(self, message: str, level: str = "info"):
        """
        输出日志消息

        Args:
            message: 日志消息
            level: 日志级别 ('info', 'success', 'warning', 'error')
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        color_map = {
            "info": ft.Colors.WHITE,
            "success": ft.Colors.GREEN_400,
            "warning": ft.Colors.ORANGE_400,
            "error": ft.Colors.RED_400,
        }
        color = color_map.get(level, ft.Colors.WHITE)

        prefix_map = {"info": "›", "success": "✓", "warning": "⚠", "error": "✗"}
        prefix = prefix_map.get(level, "›")

        log_entry = ft.Row(
            [
                ft.Text(
                    f"[{timestamp}]",
                    size=self.font.console,
                    color=ft.Colors.WHITE54,
                    font_family="Consolas",
                    selectable=True,
                ),
                ft.Text(
                    prefix,
                    size=self.font.console,
                    color=color,
                    selectable=True,
                ),
                ft.Text(
                    message,
                    size=self.font.console,
                    color=color,
                    font_family="Consolas",
                    selectable=True,
                ),
            ],
            spacing=8,
        )

        self.output.controls.append(log_entry)
        if len(self.output.controls) > CONSOLE_MAX_LINES:
            self.output.controls.pop(0)

    def update_texts(self, t_func):
        """更新语言"""
        self.t = t_func
        self.header_text.value = self.t("console_output")
