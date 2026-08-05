"""多源图片服务 (Unsplash + Pexels)

提供统一的图片搜索接口，支持 Unsplash 和 Pexels 两个图片源。
通过 provider 参数切换来源：
  - "auto"：优先可用源，失败自动降级到备选源
  - "unsplash"：仅使用 Unsplash
  - "pexels"：仅使用 Pexels
"""

import requests
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict, Any
from ..config import get_settings


# ============ 统一图片数据结构 ============

def _make_photo(
    *,
    id: str,
    url: str,
    thumb: Optional[str] = None,
    description: Optional[str] = None,
    photographer: Optional[str] = None,
    source: str = "unknown",
) -> Dict[str, Any]:
    """构造标准化图片字典"""
    return {
        "id": id,
        "url": url,
        "thumb": thumb,
        "description": description,
        "photographer": photographer,
        "source": source,
    }


# ============ Provider 基类 ============

class ImageProvider(ABC):
    """图片提供商抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """提供商名称"""

    @abstractmethod
    def is_configured(self) -> bool:
        """API Key 是否已配置"""

    @abstractmethod
    def search_photos(self, query: str, per_page: int = 5) -> List[Dict[str, Any]]:
        """搜索图片，返回标准化字典列表"""


# ============ Unsplash 提供商 ============

class UnsplashProvider(ImageProvider):
    """Unsplash 图片提供商"""

    def __init__(self, access_key: str):
        self._access_key = access_key
        self._base_url = "https://api.unsplash.com"

    @property
    def name(self) -> str:
        return "unsplash"

    def is_configured(self) -> bool:
        return bool(self._access_key)

    def search_photos(self, query: str, per_page: int = 5) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []
        try:
            response = requests.get(
                f"{self._base_url}/search/photos",
                params={
                    "query": query,
                    "per_page": per_page,
                    "client_id": self._access_key,
                },
                timeout=10,
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            return [
                _make_photo(
                    id=photo.get("id", ""),
                    url=photo.get("urls", {}).get("regular", ""),
                    thumb=photo.get("urls", {}).get("thumb"),
                    description=photo.get("description") or photo.get("alt_description"),
                    photographer=photo.get("user", {}).get("name"),
                    source="unsplash",
                )
                for photo in results
            ]
        except Exception as e:
            print(f"Unsplash搜索失败: {e}")
            return []


# ============ Pexels 提供商 ============

class PexelsProvider(ImageProvider):
    """Pexels 图片提供商"""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://api.pexels.com/v1"

    @property
    def name(self) -> str:
        return "pexels"

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def search_photos(self, query: str, per_page: int = 5) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []
        try:
            response = requests.get(
                f"{self._base_url}/search",
                params={
                    "query": query,
                    "per_page": per_page,
                },
                headers={"Authorization": self._api_key},
                timeout=10,
            )
            response.raise_for_status()
            photos_data = response.json().get("photos", [])
            return [
                _make_photo(
                    id=str(photo.get("id", "")),
                    url=photo.get("src", {}).get("large", ""),
                    thumb=photo.get("src", {}).get("medium"),
                    description=photo.get("alt"),
                    photographer=photo.get("photographer"),
                    source="pexels",
                )
                for photo in photos_data
            ]
        except Exception as e:
            print(f"Pexels搜索失败: {e}")
            return []


# ============ 统一图片服务 ============

class ImageService:
    """多源图片服务

    支持 Unsplash 和 Pexels，可通过 provider 参数选择来源:
      - "auto"  (默认): 按优先级尝试所有已配置的源，失败自动降级
      - "unsplash": 仅使用 Unsplash
      - "pexels":   仅使用 Pexels
    """

    def __init__(self):
        settings = get_settings()
        self._providers: Dict[str, ImageProvider] = {}
        self._priority: List[str] = []  # 有序优先级列表
        self._url_cache: Dict[str, str] = {}

        # 注册提供商
        unsplash = UnsplashProvider(settings.unsplash_access_key)
        pexels = PexelsProvider(settings.pexels_api_key)

        if unsplash.is_configured():
            self._providers["unsplash"] = unsplash
            self._priority.append("unsplash")
        if pexels.is_configured():
            self._providers["pexels"] = pexels
            self._priority.append("pexels")

        # 打印可用源信息
        if self._priority:
            print(f"图片服务初始化完成，可用源: {', '.join(self._priority)}")
        else:
            print("警告: 没有配置任何图片API密钥，景点配图功能不可用")

    # ---- 向下兼容属性 ----
    @property
    def access_key(self) -> str:
        """兼容旧代码检查 access_key"""
        unsplash = self._providers.get("unsplash")
        if isinstance(unsplash, UnsplashProvider):
            return unsplash._access_key
        return ""

    @property
    def available_providers(self) -> List[str]:
        """返回当前已配置的提供商名称列表"""
        return list(self._priority)

    # ---- 核心方法 ----

    def _resolve_providers(self, provider: str) -> List[ImageProvider]:
        """根据 provider 参数解析要尝试的提供商列表"""
        if provider == "auto":
            return [self._providers[name] for name in self._priority]
        elif provider in self._providers:
            return [self._providers[provider]]
        else:
            print(f"未知的图片来源 '{provider}'，回退到 auto 模式")
            return [self._providers[name] for name in self._priority]

    def search_photos(self, query: str, per_page: int = 5, provider: str = "auto") -> List[Dict[str, Any]]:
        """搜索图片

        Args:
            query: 搜索关键词
            per_page: 每页数量
            provider: 图片来源 ("auto" / "unsplash" / "pexels")

        Returns:
            标准化图片字典列表
        """
        for p in self._resolve_providers(provider):
            results = p.search_photos(query, per_page)
            if results:
                return results
        return []

    def get_photo_url(self, query: str, provider: str = "auto") -> Optional[str]:
        """获取单张图片 URL

        Args:
            query: 搜索关键词
            provider: 图片来源

        Returns:
            图片 URL 或 None
        """
        cache_key = f"{provider}:{query}"
        if cache_key in self._url_cache:
            return self._url_cache[cache_key]

        photos = self.search_photos(query, per_page=1, provider=provider)
        if photos:
            url = photos[0].get("url")
            if url:
                self._url_cache[cache_key] = url
                return url
        return None

    def enrich_trip_plan_images(self, plan, city: str, max_workers: int = 2, provider: str = "auto"):
        """为缺失图片的景点填充配图

        失败不会导致程序中断：没有获取到照片的景点将保持 image_url=None。

        Args:
            plan: 行程计划对象
            city: 城市名称
            max_workers: 并发线程数
            provider: 图片来源
        """
        if not self._priority:
            print("未配置任何图片API密钥，跳过景点配图")
            return plan

        tasks = []
        for day in plan.days:
            for attraction in day.attractions:
                if not attraction.image_url:
                    tasks.append((city, attraction))

        if not tasks:
            return plan

        def fetch(task):
            task_city, attraction = task
            try:
                query = f"{attraction.name} {task_city}".strip()
                attraction.image_url = self.get_photo_url(query, provider=provider)
            except Exception as e:
                print(f"景点配图失败: {attraction.name}: {e}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(fetch, tasks))

        total = sum(len(day.attractions) for day in plan.days)
        with_images = sum(
            1 for day in plan.days for attraction in day.attractions if attraction.image_url
        )
        source_label = provider if provider != "auto" else "多源"
        print(f"景点配图完成 ({source_label}): {with_images}/{total}")
        return plan


# ============ 向下兼容别名 ============

# 旧代码中 import UnsplashService 仍然可用
UnsplashService = ImageService

# ============ 单例工厂 ============

_image_service: Optional[ImageService] = None


def get_image_service() -> ImageService:
    """获取图片服务实例 (单例模式)"""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service


# 向下兼容：旧代码中 from unsplash_service import get_unsplash_service 仍可用
def get_unsplash_service() -> ImageService:
    """获取图片服务实例 (向下兼容别名)"""
    return get_image_service()
