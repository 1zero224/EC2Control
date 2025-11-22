"""
工具栏组件
"""

from collections.abc import Callable

import flet as ft
from flet import Icons


class Toolbar:
    """顶部工具栏组件"""

    def __init__(
        self,
        font,
        t_func,
        on_refresh: Callable | None = None,
        on_toggle_auto_refresh: Callable | None = None,
        on_toggle_language: Callable | None = None,
        on_toggle_theme: Callable | None = None,
        on_region_change: Callable | None = None,
        is_dark_mode: bool = True,
        current_lang: str = "en",
    ):
        """
        初始化工具栏

        Args:
            font: FontScale 实例
            t_func: 翻译函数
            on_refresh: 刷新回调
            on_toggle_auto_refresh: 切换自动刷新回调
            on_toggle_language: 切换语言回调
            on_toggle_theme: 切换主题回调
            on_region_change: 区域变更回调
            is_dark_mode: 是否暗色模式
            current_lang: 当前语言
        """
        self.font = font
        self.t = t_func
        self.on_refresh = on_refresh
        self.on_toggle_auto_refresh = on_toggle_auto_refresh
        self.on_toggle_language = on_toggle_language
        self.on_toggle_theme = on_toggle_theme
        self.on_region_change = on_region_change
        self.is_dark_mode = is_dark_mode
        self.current_lang = current_lang
        self._build()

    def _build(self):
        """构建工具栏UI"""
        # 标题
        self.title_text = ft.Text(
            self.t("app_title"),
            size=self.font.title,
            weight=ft.FontWeight.W_600,
            font_family="YaHei",
        )

        # 语言切换按钮
        self.lang_button = ft.IconButton(
            icon=Icons.TRANSLATE,
            icon_size=self.font.icon_medium,
            tooltip="English" if self.current_lang == "zh" else "中文",
            on_click=self._handle_toggle_language,
        )

        # 主题切换按钮
        self.theme_button = ft.IconButton(
            icon=Icons.LIGHT_MODE if self.is_dark_mode else Icons.DARK_MODE,
            icon_size=self.font.icon_medium,
            tooltip=self.t("theme_light") if self.is_dark_mode else self.t("theme_dark"),
            on_click=self._handle_toggle_theme,
        )

        # 区域筛选下拉框
        self.region_filter = ft.Dropdown(
            label=self.t("region_filter"),
            width=220,
            text_size=self.font.dropdown,
            options=[ft.dropdown.Option("all", self.t("all_regions"))],
            value="all",
            on_change=self._handle_region_change,
            border_color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE),
            focused_border_color=ft.Colors.PRIMARY,
            text_style=ft.TextStyle(
                font_family="YaHei", size=self.font.dropdown, weight=ft.FontWeight.W_400
            ),
            label_style=ft.TextStyle(font_family="YaHei", size=self.font.small),
        )

        # 刷新按钮文本
        self.refresh_text = ft.Text(
            self.t("refresh"),
            size=self.font.button,
            font_family="YaHei",
            weight=ft.FontWeight.W_400,
            color=ft.Colors.WHITE,
        )

        # 刷新图标
        self.refresh_icon = ft.Icon(
            Icons.REFRESH,
            size=self.font.icon_small,
            color=ft.Colors.WHITE,
            rotate=ft.Rotate(0),
            animate_rotation=ft.Animation(1000, ft.AnimationCurve.LINEAR),
        )

        # 刷新按钮
        self.refresh_button = ft.Container(
            content=ft.Row(
                [
                    self.refresh_icon,
                    self.refresh_text,
                ],
                spacing=8,
                tight=True,
            ),
            on_click=self._handle_refresh,
            bgcolor=ft.Colors.BLUE_700,
            border_radius=6,
            padding=ft.Padding(16, 12, 16, 12),
            ink=True,
        )

        # 刷新状态标志
        self._is_refreshing = False

        # 自动刷新开关
        self.auto_refresh_switch = ft.Switch(
            label=self.t("auto_refresh"),
            value=True,
            on_change=self._handle_toggle_auto_refresh,
            label_style=ft.TextStyle(font_family="YaHei", size=self.font.small),
        )

        # 工具栏行
        self.control = ft.Row(
            [
                self.title_text,
                self.lang_button,
                self.theme_button,
                ft.Container(expand=True),
                self.region_filter,
                self.auto_refresh_switch,
                self.refresh_button,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=16,
        )

    def get_control(self) -> ft.Row:
        """获取工具栏控件"""
        return self.control

    def update_region_options(self, instances: list, current_value: str = "all"):
        """更新区域筛选选项"""
        regions = set(inst["region"] for inst in instances)
        region_counts = {}
        for inst in instances:
            region = inst["region"]
            region_counts[region] = region_counts.get(region, 0) + 1

        self.region_filter.options.clear()
        self.region_filter.options.append(
            ft.dropdown.Option("all", f"{self.t('all_regions')} ({len(instances)})")
        )
        for region in sorted(regions):
            count = region_counts[region]
            self.region_filter.options.append(ft.dropdown.Option(region, f"{region} ({count})"))

        self.region_filter.value = current_value
        self.region_filter.update()

    def get_selected_region(self) -> str:
        """获取当前选中的区域"""
        return self.region_filter.value if self.region_filter.value else "all"

    def is_auto_refresh_enabled(self) -> bool:
        """获取自动刷新状态"""
        return self.auto_refresh_switch.value

    def set_refreshing(self, is_refreshing: bool):
        """
        设置刷新状态并更新 UI

        Args:
            is_refreshing: 是否正在刷新
        """
        self._is_refreshing = is_refreshing

        if is_refreshing:
            # 禁用状态：降低不透明度和更改背景色
            self.refresh_button.bgcolor = ft.Colors.BLUE_900
            self.refresh_button.opacity = 0.7
            # 启动旋转动画
            import math

            self.refresh_icon.rotate = ft.Rotate(angle=4 * math.pi)
        else:
            # 恢复正常状态
            self.refresh_button.bgcolor = ft.Colors.BLUE_700
            self.refresh_button.opacity = 1.0
            # 重置旋转
            self.refresh_icon.rotate = ft.Rotate(0)

        self.refresh_button.update()
        self.refresh_icon.update()

    def _handle_refresh(self, e):
        if self.on_refresh and not self._is_refreshing:
            self.on_refresh(e)

    def _handle_toggle_auto_refresh(self, e):
        if self.on_toggle_auto_refresh:
            self.on_toggle_auto_refresh(e)

    def _handle_toggle_language(self, e):
        if self.on_toggle_language:
            self.on_toggle_language(e)

    def _handle_toggle_theme(self, e):
        if self.on_toggle_theme:
            self.on_toggle_theme(e)

    def _handle_region_change(self, e):
        if self.on_region_change:
            self.on_region_change(e)

    def update_texts(self, t_func, current_lang: str):
        """更新语言"""
        self.t = t_func
        self.current_lang = current_lang
        self.title_text.value = self.t("app_title")
        self.lang_button.tooltip = "English" if self.current_lang == "zh" else "中文"
        self.theme_button.tooltip = (
            self.t("theme_light") if self.is_dark_mode else self.t("theme_dark")
        )
        self.refresh_text.value = self.t("refresh")
        self.auto_refresh_switch.label = self.t("auto_refresh")
        self.region_filter.label = self.t("region_filter")

    def update_theme_button(self, is_dark_mode: bool):
        """更新主题按钮状态"""
        self.is_dark_mode = is_dark_mode
        self.theme_button.icon = Icons.LIGHT_MODE if is_dark_mode else Icons.DARK_MODE
        self.theme_button.tooltip = self.t("theme_light") if is_dark_mode else self.t("theme_dark")
