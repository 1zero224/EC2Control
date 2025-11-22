"""
国际化翻译配置
"""

# 国际化翻译字典
I18N = {
    "zh": {
        "app_title": "EC2Control",
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
        "tip_pin": "置顶实例",
        "tip_unpin": "取消置顶",
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
        "log_refreshing": "正在刷新实例数据...",
        "log_refresh_success": "刷新完成，共加载 {count} 个实例",
        "log_regions_detected": "检测到 {count} 个可用区域",
        # 主题
        "theme_light": "亮色",
        "theme_dark": "暗色",
    },
    "en": {
        "app_title": "EC2Control",
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
        "tip_pin": "Pin Instance",
        "tip_unpin": "Unpin Instance",
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
        "log_refreshing": "Refreshing instances data...",
        "log_refresh_success": "Refresh complete, loaded {count} instances",
        "log_regions_detected": "Detected {count} available regions",
        # Theme
        "theme_light": "Light",
        "theme_dark": "Dark",
    },
}


def get_text(lang: str, key: str, **kwargs) -> str:
    """
    获取指定语言的翻译文本

    Args:
        lang: 语言代码 ('zh' 或 'en')
        key: 翻译键
        **kwargs: 格式化参数

    Returns:
        翻译后的文本
    """
    text = I18N.get(lang, I18N["zh"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
