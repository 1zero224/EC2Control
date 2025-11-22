"""
字体缩放系统 - 根据屏幕分辨率自适应
"""

import flet as ft

from src.utils.screen_utils import get_screen_resolution


class FontScale:
    """字体缩放系统 - 根据屏幕分辨率自适应"""

    def __init__(self, page: ft.Page):
        # 获取真实屏幕分辨率
        self.screen_width, self.screen_height = get_screen_resolution()
        # 计算基于分辨率的缩放因子（基准：1920x1080）
        width_scale = self.screen_width / 1920
        height_scale = self.screen_height / 1080
        self.scale = min(width_scale, height_scale, 1.3)

    def size(self, base_size: int) -> int:
        """计算缩放后的字体大小"""
        return int(base_size * self.scale)

    # 预定义字体大小
    @property
    def title(self) -> int:
        return self.size(26)

    @property
    def heading(self) -> int:
        return self.size(18)

    @property
    def body(self) -> int:
        return self.size(14)

    @property
    def small(self) -> int:
        return self.size(12)

    @property
    def tiny(self) -> int:
        return self.size(11)

    @property
    def console(self) -> int:
        return self.size(11)

    @property
    def table_header(self) -> int:
        return self.size(13)

    @property
    def table_cell(self) -> int:
        return self.size(12)

    @property
    def button(self) -> int:
        return self.size(14)

    @property
    def dropdown(self) -> int:
        return self.size(14)

    @property
    def icon_small(self) -> int:
        return self.size(16)

    @property
    def icon_medium(self) -> int:
        return self.size(20)
