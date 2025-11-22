"""
本地文件缓存管理器
负责实例数据和用户设置的持久化存储
"""
import json
from typing import List, Dict

from src.config.settings import CACHE_DIR, CACHE_FILE, SETTINGS_FILE


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
