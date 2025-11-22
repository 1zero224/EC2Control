"""
EC2 管理应用主类
"""
import flet as ft
import asyncio
from functools import partial

from src.config.constants import (
    FONT_FAMILY, MONO_FONT,
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, DEFAULT_PADDING,
    AUTO_REFRESH_INTERVAL, REBOOT_POLL_MAX_ATTEMPTS, REBOOT_POLL_INTERVAL
)
from src.core.ec2_service import EC2Service
from src.core.cache_manager import CacheManager
from src.ui.themes.font_scale import FontScale
from src.ui.themes.i18n import I18N, get_text
from src.ui.components.toolbar import Toolbar
from src.ui.components.instance_table import InstanceTable
from src.ui.components.console import ConsolePanel


class EC2ManagerApp:
    """EC2 管理应用主类"""

    def __init__(self, page: ft.Page):
        """初始化应用"""
        self.page = page
        self.page.window.width = DEFAULT_WINDOW_WIDTH
        self.page.window.height = DEFAULT_WINDOW_HEIGHT
        self.page.padding = DEFAULT_PADDING

        # 从本地文件读取用户偏好设置
        settings = CacheManager.load_settings()
        self.current_lang = settings.get("app_language", "zh")
        self.is_dark_mode = settings.get("app_dark_mode", True)

        # 设置主题
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT
        self.page.bgcolor = None if self.is_dark_mode else "#F4F6F9"
        self.page.title = self.t("app_title")
        self.page.fonts = {
            "YaHei": FONT_FAMILY,
            "Consolas": MONO_FONT,
        }

        # 初始化字体缩放系统
        self.font = FontScale(self.page)

        # 服务和数据
        self.ec2_service = None
        self.all_instances = []
        self.filtered_instances = []
        self.auto_refresh_task = None
        self.is_loading = False

        # 跟踪正在重启的实例（用于保持 rebooting 状态）
        self.rebooting_instances = set()  # 存储正在重启的实例 ID

        # 置顶的实例 ID 集合（持久化）
        self.pinned_instances = set(settings.get("pinned_instances", []))

        # 构建UI
        self._setup_ui()

    def t(self, key: str, **kwargs) -> str:
        """获取当前语言的翻译文本"""
        return get_text(self.current_lang, key, **kwargs)

    def _setup_ui(self):
        """构建用户界面"""
        # 工具栏
        self.toolbar = Toolbar(
            font=self.font,
            t_func=self.t,
            on_refresh=self._manual_refresh,
            on_toggle_auto_refresh=self._toggle_auto_refresh,
            on_toggle_language=self._toggle_language,
            on_toggle_theme=self._toggle_theme,
            on_region_change=self._on_region_filter_changed,
            is_dark_mode=self.is_dark_mode,
            current_lang=self.current_lang
        )

        # 实例表格
        self.instance_table = InstanceTable(
            font=self.font,
            t_func=self.t,
            on_start=self._start_instance,
            on_stop=self._stop_instance,
            on_reboot=self._reboot_instance,
            on_pin=self._toggle_pin_instance,
            on_sort=self._handle_sort_changed
        )

        # 控制台
        self.console = ConsolePanel(font=self.font, t_func=self.t)

        # 主容器
        main_container = ft.Column(
            [
                self.toolbar.get_control(),
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.15, ft.Colors.ON_SURFACE)),
                self.instance_table.get_control(),
                self.console.get_control(),
            ],
            spacing=16,
            expand=True,
        )

        self.page.add(main_container)

        # 初始化
        self._log_message(self.t("log_startup"), "info")
        self.page.run_task(self._initialize_service)

    def _log_message(self, message: str, level: str = "info"):
        """输出日志消息"""
        self.console.log(message, level)
        self.page.update()

    async def _initialize_service(self):
        """初始化 EC2 服务并加载所有区域的实例"""
        try:
            # 立即初始化 EC2 服务（不进行网络请求）
            self.ec2_service = EC2Service()
            self._log_message(self.t("log_connected", region=self.ec2_service.default_region), "success")
            self._log_message(
                self.t("log_screen_info", width=self.font.screen_width, height=self.font.screen_height, scale=self.font.scale),
                "info"
            )

            # 先加载缓存的实例列表（如果存在）- 这是最快的方式
            cached_instances = CacheManager.load_instances()
            if cached_instances:
                self.all_instances = cached_instances
                self.toolbar.update_region_options(self.all_instances)
                self._apply_filter()
                self._log_message(self.t("log_cache_loaded", count=len(cached_instances)), "info")

            # 延迟获取可用区域数量（非阻塞）
            asyncio.create_task(self._load_regions_info())

            # 后台加载最新的实例数据（非阻塞）
            asyncio.create_task(self._background_load_instances())

            # 启动自动刷新
            if self.toolbar.is_auto_refresh_enabled():
                self._start_auto_refresh()

        except Exception as e:
            self._log_message(self.t("log_init_failed", error=str(e)), "error")

    async def _load_regions_info(self):
        """后台加载区域信息（非阻塞）"""
        try:
            available_regions = await asyncio.get_event_loop().run_in_executor(
                None,
                self.ec2_service.get_available_regions
            )
            self._log_message(self.t("log_regions_detected", count=len(available_regions)), "info")
        except Exception as e:
            self._log_message(f"获取区域列表失败: {str(e)}", "warning")

    async def _background_load_instances(self):
        """后台加载实例列表（非阻塞）"""
        try:
            await self._load_all_regions()
        except Exception as e:
            self._log_message(f"后台加载实例失败: {str(e)}", "warning")

    async def _load_all_regions(self, is_manual: bool = False):
        """
        加载所有区域的实例

        Args:
            is_manual: 是否为手动刷新（用于显示刷新动画）
        """
        if self.is_loading:
            return

        self.is_loading = True

        # 如果是手动刷新，显示加载状态
        if is_manual:
            self.toolbar.set_refreshing(True)
            self._log_message(self.t("log_refreshing"), "info")

        try:
            instances = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.ec2_service.list_all_instances()
            )

            # 保持正在重启的实例的 rebooting 状态
            for inst in instances:
                if inst['id'] in self.rebooting_instances:
                    inst['state'] = 'rebooting'

            self.all_instances = instances
            CacheManager.save_instances(instances)
            self.toolbar.update_region_options(self.all_instances, self.toolbar.get_selected_region())
            self._apply_filter()

            # 如果是手动刷新，显示成功消息
            if is_manual:
                self._log_message(self.t("log_refresh_success", count=len(instances)), "success")

        except Exception as e:
            self._log_message(self.t("log_load_failed", error=str(e)), "error")
        finally:
            self.is_loading = False
            # 如果是手动刷新，恢复按钮状态
            if is_manual:
                self.toolbar.set_refreshing(False)

    def _apply_filter(self):
        """应用区域筛选"""
        selected_region = self.toolbar.get_selected_region()

        if selected_region == "all":
            self.filtered_instances = self.all_instances
        else:
            self.filtered_instances = [
                inst for inst in self.all_instances
                if inst['region'] == selected_region
            ]

        self.instance_table.update_instances(self.filtered_instances, self.pinned_instances)
        self.page.update()

    def _on_region_filter_changed(self, e):
        """区域筛选变更事件"""
        self._apply_filter()

    def _handle_sort_changed(self):
        """处理排序变更事件"""
        self._apply_filter()

    def _manual_refresh(self, e):
        """手动刷新"""
        async def manual_refresh_task():
            await self._load_all_regions(is_manual=True)
        self.page.run_task(manual_refresh_task)

    def _toggle_auto_refresh(self, e):
        """切换自动刷新"""
        if self.toolbar.is_auto_refresh_enabled():
            self._start_auto_refresh()
            self._log_message(self.t("log_auto_on"), "success")
        else:
            self._stop_auto_refresh()
            self._log_message(self.t("log_auto_off"), "warning")

    def _start_auto_refresh(self):
        """启动自动刷新"""
        if self.auto_refresh_task is None:
            self.auto_refresh_task = self.page.run_task(self._auto_refresh_loop)

    def _stop_auto_refresh(self):
        """停止自动刷新"""
        if self.auto_refresh_task:
            self.auto_refresh_task = None

    async def _auto_refresh_loop(self):
        """自动刷新循环"""
        while self.toolbar.is_auto_refresh_enabled():
            await asyncio.sleep(AUTO_REFRESH_INTERVAL)
            if self.toolbar.is_auto_refresh_enabled() and not self.is_loading:
                await self._load_all_regions()

    def _toggle_language(self, e):
        """切换语言"""
        self.current_lang = "en" if self.current_lang == "zh" else "zh"
        self._save_settings()
        self._update_ui_texts()
        self.page.update()

    def _toggle_theme(self, e):
        """切换主题"""
        self.is_dark_mode = not self.is_dark_mode
        self._save_settings()
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT
        self.page.bgcolor = None if self.is_dark_mode else "#F4F6F9"
        self.toolbar.update_theme_button(self.is_dark_mode)
        self.page.update()

    def _save_settings(self):
        """保存用户设置到本地文件"""
        settings = {
            "app_language": self.current_lang,
            "app_dark_mode": self.is_dark_mode,
            "pinned_instances": list(self.pinned_instances),
        }
        CacheManager.save_settings(settings)

    def _update_ui_texts(self):
        """更新所有UI文本为当前语言"""
        self.page.title = self.t("app_title")
        self.toolbar.update_texts(self.t, self.current_lang)
        self.toolbar.update_region_options(self.all_instances, self.toolbar.get_selected_region())
        self.instance_table.update_texts(self.t)
        self.console.update_texts(self.t)
        self._apply_filter()

    def _start_instance(self, instance_id: str, region: str):
        """启动实例"""
        try:
            self._log_message(self.t("log_starting", id=instance_id, region=region), "info")
            self.ec2_service.start_instance(instance_id, region)
            self._log_message(self.t("log_start_sent", id=instance_id), "success")

            for inst in self.all_instances:
                if inst['id'] == instance_id:
                    inst['state'] = 'pending'
            self._apply_filter()

        except Exception as e:
            self._log_message(self.t("log_start_failed", error=str(e)), "error")

    def _stop_instance(self, instance_id: str, region: str):
        """停止实例"""
        try:
            self._log_message(self.t("log_stopping", id=instance_id, region=region), "info")
            self.ec2_service.stop_instance(instance_id, region)
            self._log_message(self.t("log_stop_sent", id=instance_id), "success")

            for inst in self.all_instances:
                if inst['id'] == instance_id:
                    inst['state'] = 'stopping'
            self._apply_filter()

        except Exception as e:
            self._log_message(self.t("log_stop_failed", error=str(e)), "error")

    def _reboot_instance(self, instance_id: str, region: str):
        """重启实例"""
        reboot_success = False
        try:
            self._log_message(self.t("log_rebooting", id=instance_id, region=region), "info")
            self.ec2_service.reboot_instance(instance_id, region)
            self._log_message(self.t("log_reboot_sent", id=instance_id), "success")
            reboot_success = True
        except Exception as e:
            self._log_message(self.t("log_reboot_failed", error=str(e)), "error")
            return

        if reboot_success:
            # 添加到重启跟踪集合
            self.rebooting_instances.add(instance_id)

            # 更新本地状态
            for inst in self.all_instances:
                if inst['id'] == instance_id:
                    inst['state'] = 'rebooting'
            self._apply_filter()

            # 启动轮询任务
            async def poll_task():
                await self._poll_instance_status(instance_id, region)
            self.page.run_task(poll_task)

    def _toggle_pin_instance(self, instance_id: str, is_pinned: bool):
        """
        切换实例置顶状态

        Args:
            instance_id: 实例 ID
            is_pinned: 当前是否置顶
        """
        if is_pinned:
            # 取消置顶
            self.pinned_instances.discard(instance_id)
            self._log_message(f"已取消置顶实例 {instance_id}", "info")
        else:
            # 置顶
            self.pinned_instances.add(instance_id)
            self._log_message(f"已置顶实例 {instance_id}", "info")

        # 保存设置
        self._save_settings()

        # 刷新显示
        self._apply_filter()

    def _get_instance_status_sync(self, instance_id: str, region: str):
        """同步获取实例状态（用于 run_in_executor）"""
        return self.ec2_service.get_instance_status_checks(instance_id, region)

    async def _poll_instance_status(self, instance_id: str, region: str):
        """轮询检查实例状态，直到重启完成"""
        for attempt in range(REBOOT_POLL_MAX_ATTEMPTS):
            await asyncio.sleep(REBOOT_POLL_INTERVAL)

            try:
                status = await asyncio.get_event_loop().run_in_executor(
                    None,
                    partial(self._get_instance_status_sync, instance_id, region)
                )

                instance_state = status.get('instance_state', 'unknown')
                system_status = status.get('system_status', 'unknown')
                instance_status = status.get('instance_status', 'unknown')

                if (instance_state == 'running' and
                    system_status == 'ok' and
                    instance_status == 'ok'):

                    # 从重启跟踪集合中移除
                    self.rebooting_instances.discard(instance_id)

                    # 更新实例状态为运行中
                    for inst in self.all_instances:
                        if inst['id'] == instance_id:
                            inst['state'] = 'running'
                    self._apply_filter()
                    self._log_message(self.t("log_reboot_complete", id=instance_id, sys=system_status, inst=instance_status), "success")
                    return

                if attempt % 3 == 0:
                    self._log_message(
                        self.t("log_wait_reboot", state=instance_state, sys=system_status, inst=instance_status),
                        "info"
                    )

            except Exception as e:
                self._log_message(self.t("log_check_error", error=str(e)), "warning")

        # 超时处理
        self._log_message(self.t("log_reboot_timeout", id=instance_id), "warning")

        # 从重启跟踪集合中移除
        self.rebooting_instances.discard(instance_id)

        # 恢复为运行中状态
        for inst in self.all_instances:
            if inst['id'] == instance_id and inst['state'] == 'rebooting':
                inst['state'] = 'running'
        self._apply_filter()
