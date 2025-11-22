"""
AWS EC2 实例管理 GUI 应用
使用 Flet 框架构建的桌面应用程序
"""
import flet as ft
from flet import Icons
from ec2_service import EC2Service
from screen_utils import get_screen_resolution
import asyncio
from functools import partial
from datetime import datetime
from typing import List, Dict
import json
import os
from pathlib import Path


# 定义全局字体样式
FONT_FAMILY = "Microsoft YaHei"
MONO_FONT = "Consolas"

# 缓存目录和文件路径
CACHE_DIR = Path.home() / ".aws_ec2_gui"
CACHE_FILE = CACHE_DIR / "instances_cache.json"
SETTINGS_FILE = CACHE_DIR / "settings.json"


class CacheManager:
    """本地文件缓存管理器"""

    @staticmethod
    def ensure_cache_dir():
        """确保缓存目录存在"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_instances(instances: List[Dict]) -> bool:
        """保存实例列表到缓存文件"""
        try:
            CacheManager.ensure_cache_dir()
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(instances, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存缓存失败: {e}")
            return False

    @staticmethod
    def load_instances() -> List[Dict]:
        """从缓存文件加载实例列表"""
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    instances = json.load(f)
                    if isinstance(instances, list):
                        return instances
        except Exception as e:
            print(f"加载缓存失败: {e}")
        return []

    @staticmethod
    def save_settings(settings: Dict) -> bool:
        """保存应用设置"""
        try:
            CacheManager.ensure_cache_dir()
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False

    @staticmethod
    def load_settings() -> Dict:
        """加载应用设置"""
        try:
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if isinstance(settings, dict):
                        return settings
        except Exception as e:
            print(f"加载设置失败: {e}")
        return {}

# 国际化翻译字典
I18N = {
    "zh": {
        "app_title": "AWS EC2 实例管理器",
        "region_filter": "区域筛选",
        "all_regions": "全部区域",
        "refresh": "刷新",
        "auto_refresh": "自动刷新 (30秒)",
        "console_output": "日志",
        # 表格列头
        "col_region": "区域",
        "col_name": "实例名称",
        "col_id": "实例 ID",
        "col_state": "状态",
        "col_type": "类型",
        "col_public_ip": "公网 IP",
        "col_private_ip": "私有 IP",
        "col_action": "操作",
        # 实例状态
        "state_running": "运行中",
        "state_stopped": "已停止",
        "state_pending": "启动中",
        "state_stopping": "停止中",
        "state_rebooting": "重启中",
        "state_terminated": "已终止",
        # 操作提示
        "tip_start": "启动实例",
        "tip_stop": "停止实例",
        "tip_reboot": "重启实例",
        "tip_rebooting": "重启中...",
        # 日志消息
        "log_startup": "系统启动中...",
        "log_connected": "已连接 AWS，默认区域: {region}",
        "log_screen_info": "屏幕: {width}x{height} | 字体缩放: {scale:.2f}x",
        "log_init_failed": "初始化失败: {error}",
        "log_load_failed": "加载实例失败: {error}",
        "log_starting": "正在启动实例 {id} ({region})...",
        "log_start_sent": "实例 {id} 启动命令已发送",
        "log_start_failed": "启动失败: {error}",
        "log_stopping": "正在停止实例 {id} ({region})...",
        "log_stop_sent": "实例 {id} 停止命令已发送",
        "log_stop_failed": "停止失败: {error}",
        "log_rebooting": "正在重启实例 {id} ({region})...",
        "log_reboot_sent": "实例 {id} 重启命令已发送",
        "log_reboot_failed": "重启失败: {error}",
        "log_reboot_complete": "实例 {id} 重启完成 (系统检查: {sys}, 实例检查: {inst})",
        "log_wait_reboot": "等待重启完成... (状态: {state}, 系统: {sys}, 实例: {inst})",
        "log_check_error": "检查状态时出错: {error}",
        "log_reboot_timeout": "实例 {id} 重启状态检查超时，请手动刷新确认",
        "log_auto_on": "已启用自动刷新 (30秒)",
        "log_auto_off": "已禁用自动刷新",
        "log_cache_loaded": "已加载缓存的实例数据 ({count} 个实例)",
        # 主题
        "theme_light": "亮色",
        "theme_dark": "暗色",
    },
    "en": {
        "app_title": "AWS EC2 Instance Manager",
        "region_filter": "Region Filter",
        "all_regions": "All Regions",
        "refresh": "Refresh",
        "auto_refresh": "Auto Refresh (30s)",
        "console_output": "Logs",
        # Table columns
        "col_region": "Region",
        "col_name": "Instance Name",
        "col_id": "Instance ID",
        "col_state": "State",
        "col_type": "Type",
        "col_public_ip": "Public IP",
        "col_private_ip": "Private IP",
        "col_action": "Action",
        # Instance states
        "state_running": "Running",
        "state_stopped": "Stopped",
        "state_pending": "Pending",
        "state_stopping": "Stopping",
        "state_rebooting": "Rebooting",
        "state_terminated": "Terminated",
        # Tooltips
        "tip_start": "Start Instance",
        "tip_stop": "Stop Instance",
        "tip_reboot": "Reboot Instance",
        "tip_rebooting": "Rebooting...",
        # Log messages
        "log_startup": "System starting...",
        "log_connected": "Connected to AWS, default region: {region}",
        "log_screen_info": "Screen: {width}x{height} | Font scale: {scale:.2f}x",
        "log_init_failed": "Initialization failed: {error}",
        "log_load_failed": "Failed to load instances: {error}",
        "log_starting": "Starting instance {id} ({region})...",
        "log_start_sent": "Start command sent for instance {id}",
        "log_start_failed": "Start failed: {error}",
        "log_stopping": "Stopping instance {id} ({region})...",
        "log_stop_sent": "Stop command sent for instance {id}",
        "log_stop_failed": "Stop failed: {error}",
        "log_rebooting": "Rebooting instance {id} ({region})...",
        "log_reboot_sent": "Reboot command sent for instance {id}",
        "log_reboot_failed": "Reboot failed: {error}",
        "log_reboot_complete": "Instance {id} reboot complete (System: {sys}, Instance: {inst})",
        "log_wait_reboot": "Waiting for reboot... (State: {state}, System: {sys}, Instance: {inst})",
        "log_check_error": "Error checking status: {error}",
        "log_reboot_timeout": "Instance {id} reboot status check timeout, please refresh manually",
        "log_auto_on": "Auto refresh enabled (30s)",
        "log_auto_off": "Auto refresh disabled",
        "log_cache_loaded": "Loaded cached instances data ({count} instances)",
        # Theme
        "theme_light": "Light",
        "theme_dark": "Dark",
    }
}


class FontScale:
    """字体缩放系统 - 根据屏幕分辨率自适应"""

    def __init__(self, page: ft.Page):
        # 获取真实屏幕分辨率
        self.screen_width, self.screen_height = get_screen_resolution()
        # 计算基于分辨率的缩放因子（基准：1920x1080）
        width_scale = self.screen_width / 1920
        height_scale = self.screen_height / 1080
        resolution_scale = min(width_scale, height_scale)

        # 高分辨率屏幕（2K/4K）额外放大字体
        if self.screen_width >= 2560:
            self.scale = 1.15
        elif self.screen_width >= 1920:
            self.scale = 1.05
        else:
            self.scale = 1.0

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


class EC2ManagerApp:
    """EC2 管理应用主类"""

    def __init__(self, page: ft.Page):
        """初始化应用"""
        self.page = page
        self.page.window.width = 1300
        self.page.window.height = 750
        self.page.padding = 20

        # 从本地文件读取用户偏好设置
        settings = CacheManager.load_settings()
        self.current_lang = settings.get("app_language", "zh")
        self.is_dark_mode = settings.get("app_dark_mode", True)  # 默认暗色主题

        # 设置主题
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT
        self.page.title = self.t("app_title")
        self.page.fonts = {
            "YaHei": FONT_FAMILY,
            "Consolas": MONO_FONT,
        }

        # 初始化字体缩放系统
        self.font = FontScale(self.page)

        self.ec2_service = None
        self.instances_table = None
        self.console_output = None
        self.region_filter = None
        self.refresh_button = None

        # UI 控件引用（用于语言切换时更新）
        self.title_text = None
        self.lang_button = None
        self.theme_button = None
        self.console_header_text = None
        self.toolbar = None
        self.main_container = None

        # 数据存储
        self.all_instances = []
        self.filtered_instances = []
        self.auto_refresh_task = None
        self.is_loading = False

        self.setup_ui()

    def t(self, key: str, **kwargs) -> str:
        """获取当前语言的翻译文本"""
        text = I18N.get(self.current_lang, I18N["zh"]).get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

    def setup_ui(self):
        """构建用户界面"""
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
            on_click=self.toggle_language,
        )

        # 主题切换按钮
        self.theme_button = ft.IconButton(
            icon=Icons.DARK_MODE if not self.is_dark_mode else Icons.LIGHT_MODE,
            icon_size=self.font.icon_medium,
            tooltip=self.t("theme_dark") if not self.is_dark_mode else self.t("theme_light"),
            on_click=self.toggle_theme,
        )

        # 区域筛选下拉框
        self.region_filter = ft.Dropdown(
            label=self.t("region_filter"),
            width=220,
            text_size=self.font.dropdown,
            options=[ft.dropdown.Option("all", self.t("all_regions"))],
            value="all",
            on_change=self.on_region_filter_changed,
            text_style=ft.TextStyle(
                font_family="YaHei",
                size=self.font.dropdown,
                weight=ft.FontWeight.W_400
            ),
            label_style=ft.TextStyle(
                font_family="YaHei",
                size=self.font.small
            ),
        )

        # 刷新按钮文本
        self.refresh_text = ft.Text(
            self.t("refresh"),
            size=self.font.button,
            font_family="YaHei",
            weight=ft.FontWeight.W_400,
            color=ft.Colors.WHITE
        )

        # 刷新按钮
        self.refresh_button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(Icons.REFRESH, size=self.font.icon_small, color=ft.Colors.WHITE),
                    self.refresh_text,
                ],
                spacing=8,
                tight=True,
            ),
            on_click=self.manual_refresh,
            bgcolor=ft.Colors.BLUE_700,
            border_radius=6,
            padding=ft.Padding(16, 12, 16, 12),
            ink=True,
        )

        # 自动刷新开关
        self.auto_refresh_switch = ft.Switch(
            label=self.t("auto_refresh"),
            value=True,
            on_change=self.toggle_auto_refresh,
            label_style=ft.TextStyle(font_family="YaHei", size=self.font.small),
        )

        # 顶部工具栏
        self.toolbar = ft.Row(
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

        # 实例表格列头文本引用
        self.col_texts = {
            "region": ft.Text(self.t("col_region"), size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei"),
            "name": ft.Text(self.t("col_name"), size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei"),
            "id": ft.Text(self.t("col_id"), size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei"),
            "state": ft.Text(self.t("col_state"), size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei"),
            "type": ft.Text(self.t("col_type"), size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei"),
            "public_ip": ft.Text(self.t("col_public_ip"), size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei"),
            "private_ip": ft.Text(self.t("col_private_ip"), size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei"),
            "action": ft.Text(self.t("col_action"), size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei"),
        }

        # 实例表格
        self.instances_table = ft.DataTable(
            columns=[
                ft.DataColumn(self.col_texts["region"]),
                ft.DataColumn(self.col_texts["name"]),
                ft.DataColumn(self.col_texts["id"]),
                ft.DataColumn(self.col_texts["state"]),
                ft.DataColumn(self.col_texts["type"]),
                ft.DataColumn(self.col_texts["public_ip"]),
                ft.DataColumn(self.col_texts["private_ip"]),
                ft.DataColumn(self.col_texts["action"]),
            ],
            rows=[],
            border_radius=8,
            data_row_max_height=int(60 * self.font.scale),
            heading_row_height=int(50 * self.font.scale),
            column_spacing=int(24 * self.font.scale),
        )

        # 表格容器
        table_container = ft.Container(
            content=ft.Column(
                [self.instances_table],
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            expand=True,
            padding=0,
        )

        # 控制台输出
        self.console_output = ft.ListView(
            spacing=2,
            padding=10,
            auto_scroll=True,
        )

        console_height = int(130 * self.font.scale)
        console_container = ft.Container(
            content=self.console_output,
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.BLACK),
            border_radius=6,
            padding=0,
            height=console_height,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
        )

        self.console_header_text = ft.Text(
            self.t("console_output"),
            size=self.font.small,
            weight=ft.FontWeight.W_400,
            color=ft.Colors.WHITE70,
            font_family="YaHei"
        )

        console_header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(Icons.TERMINAL, size=self.font.icon_small, color=ft.Colors.GREEN_400),
                    self.console_header_text,
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.BLACK),
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=ft.border_radius.only(top_left=6, top_right=6),
        )

        console_section = ft.Column([console_header, console_container], spacing=0)

        # 主容器
        self.main_container = ft.Column(
            [
                self.toolbar,
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.15, ft.Colors.ON_SURFACE)),
                table_container,
                console_section,
            ],
            spacing=16,
            expand=True,
        )

        self.page.add(self.main_container)

        # 初始化
        self.log_message(self.t("log_startup"), "info")
        self.page.run_task(self.initialize_service)

    def toggle_language(self, e):
        """切换语言"""
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        # 保存语言设置到本地文件
        self.save_settings()
        self.update_ui_texts()
        self.page.update()

    def toggle_theme(self, e):
        """切换主题"""
        self.is_dark_mode = not self.is_dark_mode
        # 保存主题设置到本地文件
        self.save_settings()
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT

        # 更新主题按钮图标和提示
        self.theme_button.icon = Icons.LIGHT_MODE if self.is_dark_mode else Icons.DARK_MODE
        self.theme_button.tooltip = self.t("theme_light") if self.is_dark_mode else self.t("theme_dark")

        self.page.update()

    def save_settings(self):
        """保存用户设置到本地文件"""
        settings = {
            "app_language": self.current_lang,
            "app_dark_mode": self.is_dark_mode,
        }
        CacheManager.save_settings(settings)

    def update_ui_texts(self):
        """更新所有UI文本为当前语言"""
        # 更新窗口标题
        self.page.title = self.t("app_title")

        # 更新标题文本
        self.title_text.value = self.t("app_title")

        # 更新语言按钮提示
        self.lang_button.tooltip = "English" if self.current_lang == "zh" else "中文"

        # 更新主题按钮提示
        self.theme_button.tooltip = self.t("theme_light") if self.is_dark_mode else self.t("theme_dark")

        # 保存当前选中的区域值
        current_region_value = self.region_filter.value if self.region_filter.value else "all"

        # 重建区域筛选下拉框
        regions = set(inst['region'] for inst in self.all_instances)
        region_counts = {}
        for inst in self.all_instances:
            region = inst['region']
            region_counts[region] = region_counts.get(region, 0) + 1

        options = [ft.dropdown.Option("all", f"{self.t('all_regions')} ({len(self.all_instances)})")]
        for region in sorted(regions):
            count = region_counts[region]
            options.append(ft.dropdown.Option(region, f"{region} ({count})"))

        self.region_filter = ft.Dropdown(
            label=self.t("region_filter"),
            width=220,
            text_size=self.font.dropdown,
            options=options,
            value=current_region_value,
            on_change=self.on_region_filter_changed,
            text_style=ft.TextStyle(
                font_family="YaHei",
                size=self.font.dropdown,
                weight=ft.FontWeight.W_400
            ),
            label_style=ft.TextStyle(
                font_family="YaHei",
                size=self.font.small
            ),
        )

        # 更新刷新按钮文本
        self.refresh_text.value = self.t("refresh")

        # 更新自动刷新开关
        self.auto_refresh_switch.label = self.t("auto_refresh")

        # 重建工具栏
        self.toolbar.controls = [
            self.title_text,
            self.lang_button,
            self.theme_button,
            ft.Container(expand=True),
            self.region_filter,
            self.auto_refresh_switch,
            self.refresh_button,
        ]

        # 更新表格列头
        self.col_texts["region"].value = self.t("col_region")
        self.col_texts["name"].value = self.t("col_name")
        self.col_texts["id"].value = self.t("col_id")
        self.col_texts["state"].value = self.t("col_state")
        self.col_texts["type"].value = self.t("col_type")
        self.col_texts["public_ip"].value = self.t("col_public_ip")
        self.col_texts["private_ip"].value = self.t("col_private_ip")
        self.col_texts["action"].value = self.t("col_action")

        # 更新控制台标题
        self.console_header_text.value = self.t("console_output")

        # 重新渲染表格以更新状态徽章
        self.apply_filter()

    def log_message(self, message: str, level: str = "info"):
        """输出日志消息"""
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

        self.console_output.controls.append(log_entry)
        if len(self.console_output.controls) > 100:
            self.console_output.controls.pop(0)

        self.page.update()

    async def initialize_service(self):
        """初始化 EC2 服务并加载所有区域的实例"""
        try:
            self.ec2_service = EC2Service()
            self.log_message(self.t("log_connected", region=self.ec2_service.default_region), "success")
            self.log_message(
                self.t("log_screen_info", width=self.font.screen_width, height=self.font.screen_height, scale=self.font.scale),
                "info"
            )

            # 先加载缓存的实例列表（如果存在）
            cached_instances = CacheManager.load_instances()
            if cached_instances:
                self.all_instances = cached_instances
                self.update_region_filter_options()
                self.apply_filter()
                self.log_message(self.t("log_cache_loaded", count=len(cached_instances)), "info")

            # 后台加载最新的实例数据
            await self.load_all_regions()

            # 启动自动刷新
            if self.auto_refresh_switch.value:
                self.start_auto_refresh()

        except Exception as e:
            self.log_message(self.t("log_init_failed", error=str(e)), "error")

    async def load_all_regions(self):
        """加载所有区域的实例"""
        if self.is_loading:
            return

        self.is_loading = True

        try:
            instances = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.ec2_service.list_all_instances()
            )

            self.all_instances = instances

            # 保存实例列表到本地文件
            CacheManager.save_instances(instances)

            # 更新区域筛选选项
            self.update_region_filter_options()

            # 应用筛选并更新表格
            self.apply_filter()

        except Exception as e:
            self.log_message(self.t("log_load_failed", error=str(e)), "error")
        finally:
            self.is_loading = False

    def update_region_filter_options(self):
        """更新区域筛选下拉框的选项"""
        regions = set(inst['region'] for inst in self.all_instances)
        region_counts = {}
        for inst in self.all_instances:
            region = inst['region']
            region_counts[region] = region_counts.get(region, 0) + 1

        # 保存当前选中的值
        current_value = self.region_filter.value if self.region_filter.value else "all"

        # 完全清空并重建选项列表
        self.region_filter.options.clear()

        # 添加新选项
        self.region_filter.options.append(
            ft.dropdown.Option("all", f"{self.t('all_regions')} ({len(self.all_instances)})")
        )
        for region in sorted(regions):
            count = region_counts[region]
            self.region_filter.options.append(
                ft.dropdown.Option(region, f"{region} ({count})")
            )

        # 重新设置值
        self.region_filter.value = current_value
        self.region_filter.update()

    def on_region_filter_changed(self, e):
        """区域筛选变更事件"""
        self.apply_filter()

    def apply_filter(self):
        """应用区域筛选"""
        selected_region = self.region_filter.value

        if selected_region == "all":
            self.filtered_instances = self.all_instances
        else:
            self.filtered_instances = [
                inst for inst in self.all_instances
                if inst['region'] == selected_region
            ]

        self.update_instances_table()

    def update_instances_table(self):
        """更新实例表格"""
        self.instances_table.rows.clear()

        for instance in self.filtered_instances:
            state = instance['state']
            state_badge = self.create_state_badge(state)
            action_button = self.create_action_button(instance)

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(
                        instance['region'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="Consolas",
                        selectable=True
                    )),
                    ft.DataCell(ft.Text(
                        instance['name'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_500,
                        font_family="YaHei",
                        selectable=True
                    )),
                    ft.DataCell(ft.Text(
                        instance['id'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="Consolas",
                        selectable=True
                    )),
                    ft.DataCell(state_badge),
                    ft.DataCell(ft.Text(
                        instance['type'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="YaHei",
                        selectable=True
                    )),
                    ft.DataCell(ft.Text(
                        instance['public_ip'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="Consolas",
                        selectable=True
                    )),
                    ft.DataCell(ft.Text(
                        instance['private_ip'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="Consolas",
                        selectable=True
                    )),
                    ft.DataCell(action_button),
                ]
            )
            self.instances_table.rows.append(row)

        self.page.update()

    def create_state_badge(self, state: str):
        """创建状态徽章"""
        style_map = {
            'running': {"bg": ft.Colors.GREEN_800, "text": ft.Colors.WHITE, "label": self.t("state_running")},
            'stopped': {"bg": ft.Colors.RED_800, "text": ft.Colors.WHITE, "label": self.t("state_stopped")},
            'pending': {"bg": ft.Colors.AMBER_800, "text": ft.Colors.WHITE, "label": self.t("state_pending")},
            'stopping': {"bg": ft.Colors.ORANGE_800, "text": ft.Colors.WHITE, "label": self.t("state_stopping")},
            'rebooting': {"bg": ft.Colors.BLUE_800, "text": ft.Colors.WHITE, "label": self.t("state_rebooting")},
            'terminated': {"bg": ft.Colors.GREY_700, "text": ft.Colors.WHITE, "label": self.t("state_terminated")},
        }

        style = style_map.get(state, {"bg": ft.Colors.GREY_700, "text": ft.Colors.GREY_300, "label": state})

        return ft.Container(
            content=ft.Text(
                style["label"],
                size=self.font.tiny,
                weight=ft.FontWeight.W_600,
                color=style["text"],
                font_family="YaHei"
            ),
            bgcolor=style["bg"],
            padding=ft.Padding(
                int(10 * self.font.scale),
                int(4 * self.font.scale),
                int(10 * self.font.scale),
                int(4 * self.font.scale)
            ),
            border_radius=4,
        )

    def create_action_button(self, instance):
        """创建操作按钮 - 启动/停止/重启，固定宽度容器"""
        instance_id = instance['id']
        region = instance['region']
        state = instance['state']

        icon_size = self.font.icon_medium
        # 固定操作列宽度，容纳两个按钮
        action_width = int(80 * self.font.scale)

        if state in ['stopped', 'terminated']:
            # 使用 Row 包裹单个按钮，并左对齐，确保与停止按钮列对齐
            content = ft.Row(
                [
                    ft.IconButton(
                        icon=Icons.PLAY_ARROW_ROUNDED,
                        icon_color=ft.Colors.GREEN_400,
                        icon_size=icon_size,
                        tooltip=self.t("tip_start"),
                        disabled=(state == 'terminated'),
                        on_click=lambda e, iid=instance_id, r=region: self.start_instance(iid, r),
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            padding=int(8 * self.font.scale)
                        ),
                    ),
                ],
                spacing=0,
                tight=True,
                alignment=ft.MainAxisAlignment.START,
            )
        elif state == 'running':
            # running 状态显示停止和重启按钮
            content = ft.Row(
                [
                    ft.IconButton(
                        icon=Icons.STOP_ROUNDED,
                        icon_color=ft.Colors.RED_400,
                        icon_size=icon_size,
                        tooltip=self.t("tip_stop"),
                        on_click=lambda e, iid=instance_id, r=region: self.stop_instance(iid, r),
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            padding=int(8 * self.font.scale)
                        ),
                    ),
                    ft.IconButton(
                        icon=Icons.RESTART_ALT_ROUNDED,
                        icon_color=ft.Colors.ORANGE_400,
                        icon_size=icon_size,
                        tooltip=self.t("tip_reboot"),
                        on_click=lambda e, iid=instance_id, r=region: self.reboot_instance(iid, r),
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            padding=int(8 * self.font.scale)
                        ),
                    ),
                ],
                spacing=0,
                tight=True,
            )
        elif state in ['pending', 'rebooting']:
            # 使用 Row 包裹单个按钮，并左对齐
            content = ft.Row(
                [
                    ft.IconButton(
                        icon=Icons.HOURGLASS_EMPTY if state == 'rebooting' else Icons.STOP_ROUNDED,
                        icon_color=ft.Colors.BLUE_400 if state == 'rebooting' else ft.Colors.RED_400,
                        icon_size=icon_size,
                        tooltip=self.t("tip_rebooting") if state == 'rebooting' else self.t("tip_stop"),
                        disabled=True,
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            padding=int(8 * self.font.scale)
                        ),
                    ),
                ],
                spacing=0,
                tight=True,
                alignment=ft.MainAxisAlignment.START,
            )
        else:
            # 使用 Row 包裹单个按钮，并左对齐
            content = ft.Row(
                [
                    ft.IconButton(
                        icon=Icons.MORE_HORIZ,
                        icon_color=ft.Colors.GREY_500,
                        icon_size=icon_size,
                        disabled=True,
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            padding=int(8 * self.font.scale)
                        ),
                    ),
                ],
                spacing=0,
                tight=True,
                alignment=ft.MainAxisAlignment.START,
            )

        # 使用固定宽度容器包裹
        return ft.Container(
            content=content,
            width=action_width,
        )

    def start_instance(self, instance_id: str, region: str):
        """启动实例"""
        try:
            self.log_message(self.t("log_starting", id=instance_id, region=region), "info")
            self.ec2_service.start_instance(instance_id, region)
            self.log_message(self.t("log_start_sent", id=instance_id), "success")

            for inst in self.all_instances:
                if inst['id'] == instance_id:
                    inst['state'] = 'pending'
            self.apply_filter()

        except Exception as e:
            self.log_message(self.t("log_start_failed", error=str(e)), "error")

    def stop_instance(self, instance_id: str, region: str):
        """停止实例"""
        try:
            self.log_message(self.t("log_stopping", id=instance_id, region=region), "info")
            self.ec2_service.stop_instance(instance_id, region)
            self.log_message(self.t("log_stop_sent", id=instance_id), "success")

            for inst in self.all_instances:
                if inst['id'] == instance_id:
                    inst['state'] = 'stopping'
            self.apply_filter()

        except Exception as e:
            self.log_message(self.t("log_stop_failed", error=str(e)), "error")

    def reboot_instance(self, instance_id: str, region: str):
        """重启实例"""
        reboot_success = False
        try:
            self.log_message(self.t("log_rebooting", id=instance_id, region=region), "info")
            self.ec2_service.reboot_instance(instance_id, region)
            self.log_message(self.t("log_reboot_sent", id=instance_id), "success")
            reboot_success = True
        except Exception as e:
            self.log_message(self.t("log_reboot_failed", error=str(e)), "error")
            return

        # 重启命令发送成功后，更新状态并启动轮询
        if reboot_success:
            # 临时设置为重启中状态
            for inst in self.all_instances:
                if inst['id'] == instance_id:
                    inst['state'] = 'rebooting'
            self.apply_filter()

            # 启动轮询检查实例状态
            async def poll_task():
                await self.poll_instance_status(instance_id, region)
            self.page.run_task(poll_task)

    def _get_instance_status_sync(self, instance_id: str, region: str):
        """同步获取实例状态（用于 run_in_executor）"""
        return self.ec2_service.get_instance_status_checks(instance_id, region)

    async def poll_instance_status(self, instance_id: str, region: str):
        """轮询检查实例状态，直到重启完成"""
        max_attempts = 60  # 最多轮询60次（约5分钟）
        interval = 5  # 每5秒检查一次

        for attempt in range(max_attempts):
            await asyncio.sleep(interval)

            try:
                status = await asyncio.get_event_loop().run_in_executor(
                    None,
                    partial(self._get_instance_status_sync, instance_id, region)
                )

                instance_state = status.get('instance_state', 'unknown')
                system_status = status.get('system_status', 'unknown')
                instance_status = status.get('instance_status', 'unknown')

                # 检查是否重启完成：实例运行中且两项健康检查都通过
                if (instance_state == 'running' and
                    system_status == 'ok' and
                    instance_status == 'ok'):

                    # 更新本地状态
                    for inst in self.all_instances:
                        if inst['id'] == instance_id:
                            inst['state'] = 'running'
                    self.apply_filter()
                    self.log_message(self.t("log_reboot_complete", id=instance_id, sys=system_status, inst=instance_status), "success")
                    return

                # 记录当前检查状态
                if attempt % 3 == 0:  # 每15秒输出一次状态
                    self.log_message(
                        self.t("log_wait_reboot", state=instance_state, sys=system_status, inst=instance_status),
                        "info"
                    )

            except Exception as e:
                self.log_message(self.t("log_check_error", error=str(e)), "warning")

        # 超时
        self.log_message(self.t("log_reboot_timeout", id=instance_id), "warning")
        for inst in self.all_instances:
            if inst['id'] == instance_id and inst['state'] == 'rebooting':
                inst['state'] = 'running'
        self.apply_filter()

    def manual_refresh(self, e):
        """手动刷新"""
        self.page.run_task(self.load_all_regions)

    def toggle_auto_refresh(self, e):
        """切换自动刷新"""
        if self.auto_refresh_switch.value:
            self.start_auto_refresh()
            self.log_message(self.t("log_auto_on"), "success")
        else:
            self.stop_auto_refresh()
            self.log_message(self.t("log_auto_off"), "warning")

    def start_auto_refresh(self):
        """启动自动刷新"""
        if self.auto_refresh_task is None:
            self.auto_refresh_task = self.page.run_task(self.auto_refresh_loop)

    def stop_auto_refresh(self):
        """停止自动刷新"""
        if self.auto_refresh_task:
            self.auto_refresh_task = None

    async def auto_refresh_loop(self):
        """自动刷新循环"""
        while self.auto_refresh_switch.value:
            await asyncio.sleep(30)
            if self.auto_refresh_switch.value and not self.is_loading:
                await self.load_all_regions()


def main(page: ft.Page):
    """应用主入口"""
    EC2ManagerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
