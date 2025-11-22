"""
AWS EC2 实例管理 GUI 应用
使用 Flet 框架构建的桌面应用程序
"""
import flet as ft
from flet import Icons
from ec2_service import EC2Service
from screen_utils import get_screen_resolution
import asyncio
from datetime import datetime
from typing import List, Dict


# 定义全局字体样式
FONT_FAMILY = "Microsoft YaHei"
MONO_FONT = "Consolas"


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
        self.page.title = "AWS EC2 实例管理器"
        self.page.window.width = 1300
        self.page.window.height = 750
        self.page.padding = 20

        # 设置主题
        self.page.theme_mode = ft.ThemeMode.SYSTEM
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

        # 数据存储
        self.all_instances = []
        self.filtered_instances = []
        self.auto_refresh_task = None
        self.is_loading = False

        self.setup_ui()

    def setup_ui(self):
        """构建用户界面"""
        # 标题
        title = ft.Text(
            "AWS EC2 实例管理器",
            size=self.font.title,
            weight=ft.FontWeight.W_600,
            font_family="YaHei",
        )

        # 区域筛选下拉框
        self.region_filter = ft.Dropdown(
            label="区域筛选",
            width=220,
            text_size=self.font.dropdown,
            options=[ft.dropdown.Option("all", "全部区域")],
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

        # 刷新按钮
        self.refresh_button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(Icons.REFRESH, size=self.font.icon_small, color=ft.Colors.WHITE),
                    ft.Text(
                        "刷新实例列表",
                        size=self.font.button,
                        font_family="YaHei",
                        weight=ft.FontWeight.W_400,
                        color=ft.Colors.WHITE
                    ),
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
            label="自动刷新 (30秒)",
            value=True,
            on_change=self.toggle_auto_refresh,
            label_style=ft.TextStyle(font_family="YaHei", size=self.font.small),
        )

        # 顶部工具栏
        toolbar = ft.Row(
            [
                title,
                ft.Container(expand=True),
                self.region_filter,
                self.auto_refresh_switch,
                self.refresh_button,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=16,
        )

        # 实例表格
        self.instances_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("区域", size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei")),
                ft.DataColumn(ft.Text("实例名称", size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei")),
                ft.DataColumn(ft.Text("实例 ID", size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei")),
                ft.DataColumn(ft.Text("状态", size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei")),
                ft.DataColumn(ft.Text("类型", size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei")),
                ft.DataColumn(ft.Text("公网 IP", size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei")),
                ft.DataColumn(ft.Text("私有 IP", size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei")),
                ft.DataColumn(ft.Text("操作", size=self.font.table_header, weight=ft.FontWeight.W_600, font_family="YaHei")),
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

        console_header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(Icons.TERMINAL, size=self.font.icon_small, color=ft.Colors.GREEN_400),
                    ft.Text(
                        "控制台输出",
                        size=self.font.small,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.WHITE70,
                        font_family="YaHei"
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.BLACK),
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=ft.border_radius.only(top_left=6, top_right=6),
        )

        console_section = ft.Column([console_header, console_container], spacing=0)

        # 主容器
        main_container = ft.Column(
            [
                toolbar,
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.15, ft.Colors.ON_SURFACE)),
                table_container,
                console_section,
            ],
            spacing=16,
            expand=True,
        )

        self.page.add(main_container)

        # 初始化
        self.log_message("系统启动中...", "info")
        self.page.run_task(self.initialize_service)

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
                    font_family="Consolas"
                ),
                ft.Text(prefix, size=self.font.console, color=color),
                ft.Text(
                    message,
                    size=self.font.console,
                    color=color,
                    font_family="Consolas"
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
            self.log_message(f"已连接 AWS，默认区域: {self.ec2_service.default_region}", "success")
            self.log_message(
                f"屏幕: {self.font.screen_width}x{self.font.screen_height} | "
                f"字体缩放: {self.font.scale:.2f}x",
                "info"
            )

            # 加载所有区域的实例
            await self.load_all_regions()

            # 启动自动刷新
            if self.auto_refresh_switch.value:
                self.start_auto_refresh()

        except Exception as e:
            self.log_message(f"初始化失败: {str(e)}", "error")

    async def load_all_regions(self):
        """加载所有区域的实例"""
        if self.is_loading:
            return

        self.is_loading = True
        self.log_message("正在扫描所有 AWS 区域...", "info")

        def progress_callback(region, current, total):
            self.log_message(f"正在扫描 {region} ({current}/{total})", "info")

        try:
            instances = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.ec2_service.list_all_instances(progress_callback)
            )

            self.all_instances = instances
            self.log_message(f"扫描完成，共找到 {len(instances)} 个实例", "success")

            # 更新区域筛选选项
            self.update_region_filter_options()

            # 应用筛选并更新表格
            self.apply_filter()

        except Exception as e:
            self.log_message(f"加载实例失败: {str(e)}", "error")
        finally:
            self.is_loading = False

    def update_region_filter_options(self):
        """更新区域筛选下拉框的选项"""
        regions = set(inst['region'] for inst in self.all_instances)
        region_counts = {}
        for inst in self.all_instances:
            region = inst['region']
            region_counts[region] = region_counts.get(region, 0) + 1

        options = [ft.dropdown.Option("all", f"全部区域 ({len(self.all_instances)})")]
        for region in sorted(regions):
            count = region_counts[region]
            options.append(ft.dropdown.Option(region, f"{region} ({count})"))

        self.region_filter.options = options
        self.page.update()

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
                        font_family="Consolas"
                    )),
                    ft.DataCell(ft.Text(
                        instance['name'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_500,
                        font_family="YaHei"
                    )),
                    ft.DataCell(ft.Text(
                        instance['id'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="Consolas"
                    )),
                    ft.DataCell(state_badge),
                    ft.DataCell(ft.Text(
                        instance['type'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="YaHei"
                    )),
                    ft.DataCell(ft.Text(
                        instance['public_ip'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="Consolas"
                    )),
                    ft.DataCell(ft.Text(
                        instance['private_ip'],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="Consolas"
                    )),
                    ft.DataCell(action_button),
                ]
            )
            self.instances_table.rows.append(row)

        self.page.update()

    def create_state_badge(self, state: str):
        """创建状态徽章"""
        style_map = {
            'running': {"bg": ft.Colors.GREEN_800, "text": ft.Colors.GREEN_100, "label": "运行中"},
            'stopped': {"bg": ft.Colors.RED_800, "text": ft.Colors.RED_100, "label": "已停止"},
            'pending': {"bg": ft.Colors.AMBER_800, "text": ft.Colors.AMBER_100, "label": "启动中"},
            'stopping': {"bg": ft.Colors.ORANGE_800, "text": ft.Colors.ORANGE_100, "label": "停止中"},
            'terminated': {"bg": ft.Colors.GREY_700, "text": ft.Colors.GREY_300, "label": "已终止"},
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
        """创建操作按钮 - 只显示启动或停止"""
        instance_id = instance['id']
        region = instance['region']
        state = instance['state']

        icon_size = self.font.icon_medium

        if state in ['stopped', 'terminated']:
            return ft.IconButton(
                icon=Icons.PLAY_ARROW_ROUNDED,
                icon_color=ft.Colors.GREEN_400,
                icon_size=icon_size,
                tooltip="启动实例",
                disabled=(state == 'terminated'),
                on_click=lambda e, iid=instance_id, r=region: self.start_instance(iid, r),
                style=ft.ButtonStyle(
                    shape=ft.CircleBorder(),
                    padding=int(8 * self.font.scale)
                ),
            )
        elif state in ['running', 'pending']:
            return ft.IconButton(
                icon=Icons.STOP_ROUNDED,
                icon_color=ft.Colors.RED_400,
                icon_size=icon_size,
                tooltip="停止实例",
                disabled=(state == 'pending'),
                on_click=lambda e, iid=instance_id, r=region: self.stop_instance(iid, r),
                style=ft.ButtonStyle(
                    shape=ft.CircleBorder(),
                    padding=int(8 * self.font.scale)
                ),
            )
        else:
            return ft.IconButton(
                icon=Icons.MORE_HORIZ,
                icon_color=ft.Colors.GREY_500,
                icon_size=icon_size,
                disabled=True,
                style=ft.ButtonStyle(
                    shape=ft.CircleBorder(),
                    padding=int(8 * self.font.scale)
                ),
            )

    def start_instance(self, instance_id: str, region: str):
        """启动实例"""
        try:
            self.log_message(f"正在启动实例 {instance_id} ({region})...", "info")
            self.ec2_service.start_instance(instance_id, region)
            self.log_message(f"实例 {instance_id} 启动命令已发送", "success")

            for inst in self.all_instances:
                if inst['id'] == instance_id:
                    inst['state'] = 'pending'
            self.apply_filter()

        except Exception as e:
            self.log_message(f"启动失败: {str(e)}", "error")

    def stop_instance(self, instance_id: str, region: str):
        """停止实例"""
        try:
            self.log_message(f"正在停止实例 {instance_id} ({region})...", "info")
            self.ec2_service.stop_instance(instance_id, region)
            self.log_message(f"实例 {instance_id} 停止命令已发送", "success")

            for inst in self.all_instances:
                if inst['id'] == instance_id:
                    inst['state'] = 'stopping'
            self.apply_filter()

        except Exception as e:
            self.log_message(f"停止失败: {str(e)}", "error")

    def manual_refresh(self, e):
        """手动刷新"""
        self.page.run_task(self.load_all_regions)

    def toggle_auto_refresh(self, e):
        """切换自动刷新"""
        if self.auto_refresh_switch.value:
            self.start_auto_refresh()
            self.log_message("已启用自动刷新 (30秒)", "success")
        else:
            self.stop_auto_refresh()
            self.log_message("已禁用自动刷新", "warning")

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
                self.log_message("自动刷新中...", "info")
                await self.load_all_regions()


def main(page: ft.Page):
    """应用主入口"""
    EC2ManagerApp(page)


if __name__ == "__main__":
    ft.app(target=main)
