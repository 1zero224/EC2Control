"""
实例表格组件
"""

from collections.abc import Callable

import flet as ft
from flet import Icons


class InstanceTable:
    """EC2实例表格组件"""

    def __init__(
        self,
        font,
        t_func,
        on_start: Callable | None = None,
        on_stop: Callable | None = None,
        on_reboot: Callable | None = None,
        on_pin: Callable | None = None,
        on_sort: Callable | None = None,
    ):
        """
        初始化实例表格

        Args:
            font: FontScale 实例
            t_func: 翻译函数
            on_start: 启动实例回调
            on_stop: 停止实例回调
            on_reboot: 重启实例回调
            on_pin: 置顶/取消置顶实例回调
            on_sort: 排序变更回调
        """
        self.font = font
        self.t = t_func
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_reboot = on_reboot
        self.on_pin = on_pin
        self.on_sort = on_sort

        # 排序状态
        self.sort_column = None  # 当前排序列
        self.sort_ascending = True  # 排序方向

        self._build()

    def _build(self):
        """构建表格UI"""

        # 表格列头文本引用
        def create_header_label(text):
            return ft.Container(
                content=ft.Text(
                    text,
                    size=self.font.table_header,
                    weight=ft.FontWeight.W_600,
                    font_family="YaHei",
                    text_align=ft.TextAlign.LEFT,
                ),
                alignment=ft.alignment.center_left,
            )

        self.col_texts = {
            "region": create_header_label(self.t("col_region")),
            "name": create_header_label(self.t("col_name")),
            "id": create_header_label(self.t("col_id")),
            "state": create_header_label(self.t("col_state")),
            "type": create_header_label(self.t("col_type")),
            "public_ip": create_header_label(self.t("col_public_ip")),
            "private_ip": create_header_label(self.t("col_private_ip")),
            "action": create_header_label(self.t("col_action")),
        }

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    self.col_texts["region"], on_sort=lambda e: self._handle_sort("region")
                ),
                ft.DataColumn(self.col_texts["name"], on_sort=lambda e: self._handle_sort("name")),
                ft.DataColumn(self.col_texts["id"], on_sort=lambda e: self._handle_sort("id")),
                ft.DataColumn(
                    self.col_texts["state"], on_sort=lambda e: self._handle_sort("state")
                ),
                ft.DataColumn(self.col_texts["type"], on_sort=lambda e: self._handle_sort("type")),
                ft.DataColumn(self.col_texts["public_ip"]),
                ft.DataColumn(self.col_texts["private_ip"]),
                ft.DataColumn(self.col_texts["action"]),
            ],
            rows=[],
            border_radius=8,
            data_row_max_height=int(60 * self.font.scale),
            heading_row_height=int(50 * self.font.scale),
            column_spacing=int(24 * self.font.scale),
            sort_column_index=None,
            sort_ascending=True,
        )

    def get_control(self) -> ft.Container:
        """获取表格容器控件"""
        return ft.Container(
            content=ft.Column(
                [self.table],
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            expand=True,
            padding=0,
        )

    def update_instances(self, instances: list[dict], pinned_instances: set = None):
        """
        更新表格数据

        Args:
            instances: 实例列表
            pinned_instances: 置顶的实例 ID 集合
        """
        self.table.rows.clear()

        if pinned_instances is None:
            pinned_instances = set()

        # 分离置顶和非置顶实例
        pinned = [inst for inst in instances if inst["id"] in pinned_instances]
        unpinned = [inst for inst in instances if inst["id"] not in pinned_instances]

        # 对非置顶实例进行排序
        if self.sort_column:
            unpinned = self._sort_instances(unpinned, self.sort_column, self.sort_ascending)

        # 合并：置顶实例在前，非置顶实例在后
        sorted_instances = pinned + unpinned

        for instance in sorted_instances:
            is_pinned = instance["id"] in pinned_instances
            state = instance["state"]
            state_badge = self._create_state_badge(state)
            action_button = self._create_action_button(instance, is_pinned)

            # 区域单元格
            region_content = ft.Row(
                [
                    (
                        ft.Icon(Icons.PUSH_PIN, size=self.font.icon_small, color=ft.Colors.PRIMARY)
                        if is_pinned
                        else ft.Container(width=0)
                    ),
                    ft.Text(
                        instance["region"],
                        size=self.font.table_cell,
                        weight=ft.FontWeight.W_400,
                        font_family="Consolas",
                        selectable=True,
                    ),
                ],
                spacing=4,
                tight=True,
            )

            row = ft.DataRow(
                cells=[
                    ft.DataCell(region_content),
                    ft.DataCell(
                        ft.Text(
                            instance["name"],
                            size=self.font.table_cell,
                            weight=ft.FontWeight.W_500,
                            font_family="YaHei",
                            selectable=True,
                        )
                    ),
                    ft.DataCell(
                        ft.Text(
                            instance["id"],
                            size=self.font.table_cell,
                            weight=ft.FontWeight.W_400,
                            font_family="Consolas",
                            selectable=True,
                        )
                    ),
                    ft.DataCell(state_badge),
                    ft.DataCell(
                        ft.Text(
                            instance["type"],
                            size=self.font.table_cell,
                            weight=ft.FontWeight.W_400,
                            font_family="YaHei",
                            selectable=True,
                        )
                    ),
                    ft.DataCell(
                        ft.Text(
                            instance["public_ip"],
                            size=self.font.table_cell,
                            weight=ft.FontWeight.W_400,
                            font_family="Consolas",
                            selectable=True,
                        )
                    ),
                    ft.DataCell(
                        ft.Text(
                            instance["private_ip"],
                            size=self.font.table_cell,
                            weight=ft.FontWeight.W_400,
                            font_family="Consolas",
                            selectable=True,
                        )
                    ),
                    ft.DataCell(action_button),
                ]
            )
            self.table.rows.append(row)

    def _create_state_badge(self, state: str) -> ft.Container:
        """创建状态徽章"""
        style_map = {
            "running": {
                "bg": ft.Colors.GREEN_800,
                "text": ft.Colors.WHITE,
                "label": self.t("state_running"),
            },
            "stopped": {
                "bg": ft.Colors.RED_800,
                "text": ft.Colors.WHITE,
                "label": self.t("state_stopped"),
            },
            "pending": {
                "bg": ft.Colors.AMBER_800,
                "text": ft.Colors.WHITE,
                "label": self.t("state_pending"),
            },
            "stopping": {
                "bg": ft.Colors.ORANGE_800,
                "text": ft.Colors.WHITE,
                "label": self.t("state_stopping"),
            },
            "rebooting": {
                "bg": ft.Colors.BLUE_800,
                "text": ft.Colors.WHITE,
                "label": self.t("state_rebooting"),
            },
            "terminated": {
                "bg": ft.Colors.GREY_700,
                "text": ft.Colors.WHITE,
                "label": self.t("state_terminated"),
            },
        }

        style = style_map.get(
            state, {"bg": ft.Colors.GREY_700, "text": ft.Colors.GREY_300, "label": state}
        )

        return ft.Container(
            content=ft.Text(
                style["label"],
                size=self.font.tiny,
                weight=ft.FontWeight.W_600,
                color=style["text"],
                font_family="YaHei",
            ),
            bgcolor=style["bg"],
            padding=ft.Padding(
                int(10 * self.font.scale),
                int(4 * self.font.scale),
                int(10 * self.font.scale),
                int(4 * self.font.scale),
            ),
            border_radius=4,
        )

    def _create_action_button(self, instance: dict, is_pinned: bool = False) -> ft.Container:
        """
        创建操作按钮

        Args:
            instance: 实例信息
            is_pinned: 是否已置顶
        """
        instance_id = instance["id"]
        region = instance["region"]
        state = instance["state"]

        icon_size = self.font.icon_medium
        action_width = int(120 * self.font.scale)  # 增加宽度以容纳置顶按钮

        # 置顶按钮（始终显示）
        pin_button = ft.IconButton(
            icon=Icons.PUSH_PIN if is_pinned else Icons.PUSH_PIN_OUTLINED,
            icon_color=ft.Colors.PRIMARY if is_pinned else ft.Colors.GREY_500,
            icon_size=icon_size,
            tooltip=self.t("tip_unpin") if is_pinned else self.t("tip_pin"),
            on_click=lambda e, iid=instance_id: self._handle_pin(iid, is_pinned),
            style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=int(8 * self.font.scale)),
        )

        if state in ["stopped", "terminated"]:
            buttons = [
                ft.IconButton(
                    icon=Icons.PLAY_ARROW_ROUNDED,
                    icon_color=ft.Colors.GREEN_400,
                    icon_size=icon_size,
                    tooltip=self.t("tip_start"),
                    disabled=(state == "terminated"),
                    on_click=lambda e, iid=instance_id, r=region: self._handle_start(iid, r),
                    style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=int(8 * self.font.scale)),
                ),
                pin_button,
            ]
            content = ft.Row(buttons, spacing=0, tight=True, alignment=ft.MainAxisAlignment.START)
        elif state == "running":
            buttons = [
                ft.IconButton(
                    icon=Icons.STOP_ROUNDED,
                    icon_color=ft.Colors.RED_400,
                    icon_size=icon_size,
                    tooltip=self.t("tip_stop"),
                    on_click=lambda e, iid=instance_id, r=region: self._handle_stop(iid, r),
                    style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=int(8 * self.font.scale)),
                ),
                ft.IconButton(
                    icon=Icons.RESTART_ALT_ROUNDED,
                    icon_color=ft.Colors.ORANGE_400,
                    icon_size=icon_size,
                    tooltip=self.t("tip_reboot"),
                    on_click=lambda e, iid=instance_id, r=region: self._handle_reboot(iid, r),
                    style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=int(8 * self.font.scale)),
                ),
                pin_button,
            ]
            content = ft.Row(buttons, spacing=0, tight=True)
        elif state in ["pending", "rebooting", "stopping"]:
            buttons = [
                ft.IconButton(
                    icon=Icons.HOURGLASS_EMPTY if state == "rebooting" else Icons.STOP_ROUNDED,
                    icon_color=ft.Colors.BLUE_400 if state == "rebooting" else ft.Colors.RED_400,
                    icon_size=icon_size,
                    tooltip=self.t("tip_rebooting") if state == "rebooting" else self.t("tip_stop"),
                    disabled=True,
                    style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=int(8 * self.font.scale)),
                ),
                pin_button,
            ]
            content = ft.Row(buttons, spacing=0, tight=True, alignment=ft.MainAxisAlignment.START)
        else:
            buttons = [
                ft.IconButton(
                    icon=Icons.MORE_HORIZ,
                    icon_color=ft.Colors.GREY_500,
                    icon_size=icon_size,
                    disabled=True,
                    style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=int(8 * self.font.scale)),
                ),
                pin_button,
            ]
            content = ft.Row(buttons, spacing=0, tight=True, alignment=ft.MainAxisAlignment.START)

        return ft.Container(
            content=content,
            width=action_width,
        )

    def _handle_start(self, instance_id: str, region: str):
        """处理启动事件"""
        if self.on_start:
            self.on_start(instance_id, region)

    def _handle_stop(self, instance_id: str, region: str):
        """处理停止事件"""
        if self.on_stop:
            self.on_stop(instance_id, region)

    def _handle_reboot(self, instance_id: str, region: str):
        """处理重启事件"""
        if self.on_reboot:
            self.on_reboot(instance_id, region)

    def _handle_pin(self, instance_id: str, is_pinned: bool):
        """处理置顶/取消置顶事件"""
        if self.on_pin:
            self.on_pin(instance_id, is_pinned)

    def _handle_sort(self, column: str):
        """
        处理排序事件

        Args:
            column: 排序列名
        """
        # 切换排序方向
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True

        # 更新表格排序指示器
        column_index_map = {
            "region": 0,
            "name": 1,
            "id": 2,
            "state": 3,
            "type": 4,
        }
        self.table.sort_column_index = column_index_map.get(column)
        self.table.sort_ascending = self.sort_ascending

        # 通知应用层重新渲染数据
        if self.on_sort:
            self.on_sort()

    def _sort_instances(self, instances: list[dict], column: str, ascending: bool) -> list[dict]:
        """
        对实例列表进行排序

        Args:
            instances: 实例列表
            column: 排序列名
            ascending: 是否升序

        Returns:
            排序后的实例列表
        """
        # 状态排序优先级映射
        state_priority = {
            "running": 1,
            "rebooting": 2,
            "pending": 3,
            "stopping": 4,
            "stopped": 5,
            "terminated": 6,
        }

        def get_sort_key(inst):
            value = inst.get(column, "")
            # 特殊处理状态排序
            if column == "state":
                return state_priority.get(value, 99)
            # 处理 N/A 和空值
            if value == "N/A" or value == "":
                return chr(0xFFFF) if ascending else chr(0)  # 放到最后或最前
            return str(value).lower()

        return sorted(instances, key=get_sort_key, reverse=not ascending)

    def update_texts(self, t_func):
        """更新语言"""
        self.t = t_func
        # 更新列头文本（列头是 Container 包裹的 Text 对象）
        self.col_texts["region"].content.value = self.t("col_region")
        self.col_texts["name"].content.value = self.t("col_name")
        self.col_texts["id"].content.value = self.t("col_id")
        self.col_texts["state"].content.value = self.t("col_state")
        self.col_texts["type"].content.value = self.t("col_type")
        self.col_texts["public_ip"].content.value = self.t("col_public_ip")
        self.col_texts["private_ip"].content.value = self.t("col_private_ip")
        self.col_texts["action"].content.value = self.t("col_action")
