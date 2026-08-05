"""Unsplash图片服务"""

import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from ..config import get_settings

class UnsplashService:
    """Unsplash图片服务类"""
    
    def __init__(self):
        """初始化服务"""
        settings = get_settings()
        self.access_key = settings.unsplash_access_key
        self.base_url = "https://api.unsplash.com"
        self._url_cache = {}
    
    def search_photos(self, query: str, per_page: int = 5) -> List[dict]:
        """
        搜索图片
        
        Args:
            query: 搜索关键词
            per_page: 每页数量
            
        Returns:
            图片列表
        """
        try:
            url = f"{self.base_url}/search/photos"
            params = {
                "query": query,
                "per_page": per_page,
                "client_id": self.access_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            # 提取图片URL
            photos = []
            for photo in results:
                photos.append({
                    "id": photo.get("id"),
                    "url": photo.get("urls", {}).get("regular"),
                    "thumb": photo.get("urls", {}).get("thumb"),
                    "description": photo.get("description") or photo.get("alt_description"),
                    "photographer": photo.get("user", {}).get("name")
                })
            
            return photos
            
        except Exception as e:
            print(f"Unsplash搜索失败: {str(e)}")
            return []
    
    def get_photo_url(self, query: str) -> Optional[str]:
        """
        获取单张图片URL

        Args:
            query: 搜索关键词

        Returns:
            图片URL
        """
        if query in self._url_cache:
            return self._url_cache[query]

        photos = self.search_photos(query, per_page=1)
        if photos:
            url = photos[0].get("url")
            self._url_cache[query] = url
            return url
        return None

    def enrich_trip_plan_images(self, plan, city: str, max_workers: int = 2):
        """
        为缺失图片的景点从 Unsplash 填充配图。
        
        失败不会导致程序中断：没有获取到照片的景点将保持 image_url=None。
        """
        if not self.access_key:
            print("Unsplash ACCESS_KEY 未配置，跳过景点配图")
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
                attraction.image_url = self.get_photo_url(query)
            except Exception as e:
                print(f"Unsplash景点配图失败: {attraction.name}: {e}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(fetch, tasks))

        total = sum(len(day.attractions) for day in plan.days)
        with_images = sum(
            1 for day in plan.days for attraction in day.attractions if attraction.image_url
        )
        print(f"Unsplash景点配图完成: {with_images}/{total}")
        return plan


# 全局服务实例
_unsplash_service = None


def get_unsplash_service() -> UnsplashService:
    """获取Unsplash服务实例(单例模式)"""
    global _unsplash_service
    
    if _unsplash_service is None:
        _unsplash_service = UnsplashService()
    
    return _unsplash_service

