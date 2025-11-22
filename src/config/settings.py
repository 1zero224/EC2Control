"""
应用设置路径配置
"""
from pathlib import Path

# 缓存目录和文件路径
CACHE_DIR = Path.home() / ".aws_ec2_gui"
CACHE_FILE = CACHE_DIR / "instances_cache.json"
SETTINGS_FILE = CACHE_DIR / "settings.json"
