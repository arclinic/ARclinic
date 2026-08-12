"""
Адаптер YouTube: Data API v3 для информации о канале и видео.
"""

import os
from typing import Optional, Dict, Any


class YouTubeAdapter:
    """Работа с YouTube Data API v3."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY", "")
        self.youtube = None

    def _get_service(self):
        """Ленивая инициализация API клиента."""
        if self.youtube is None and self.api_key:
            try:
                from googleapiclient.discovery import build
                self.youtube = build("youtube", "v3", developerKey=self.api_key)
            except ImportError:
                pass
        return self.youtube

    def get_channel_stats(self, handle: str = "@arclinic") -> dict:
        """Статистика канала."""
        yt = self._get_service()
        if not yt:
            return {"error": "google-api-python-client не установлен или нет API ключа"}

        try:
            resp = yt.channels().list(part="statistics,snippet",
                                      forHandle=handle).execute()
            if resp.get("items"):
                item = resp["items"][0]
                stats = item["statistics"]
                return {
                    "title": item["snippet"]["title"],
                    "subscribers": int(stats.get("subscriberCount", 0)),
                    "total_views": int(stats.get("viewCount", 0)),
                    "total_videos": int(stats.get("videoCount", 0)),
                }
            return {"error": "Канал не найден"}
        except Exception as e:
            return {"error": str(e)}

    def get_video_stats(self, video_id: str) -> dict:
        """Статистика видео."""
        yt = self._get_service()
        if not yt:
            return {"error": "google-api-python-client не установлен"}

        try:
            resp = yt.videos().list(part="statistics,snippet",
                                    id=video_id).execute()
            if resp.get("items"):
                item = resp["items"][0]
                stats = item["statistics"]
                return {
                    "title": item["snippet"]["title"],
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "published": item["snippet"]["publishedAt"],
                }
            return {"error": "Видео не найдено"}
        except Exception as e:
            return {"error": str(e)}

    def search_channel_videos(self, channel_id: str,
                              max_results: int = 10) -> list:
        """Поиск последних видео канала."""
        yt = self._get_service()
        if not yt:
            return []

        try:
            search_resp = yt.search().list(
                part="id", channelId=channel_id, maxResults=max_results,
                order="date", type="video",
            ).execute()

            video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
            if not video_ids:
                return []

            videos_resp = yt.videos().list(
                part="statistics,snippet", id=",".join(video_ids),
            ).execute()

            results = []
            for item in videos_resp.get("items", []):
                s = item["statistics"]
                results.append({
                    "id": item["id"],
                    "title": item["snippet"]["title"],
                    "views": int(s.get("viewCount", 0)),
                    "likes": int(s.get("likeCount", 0)),
                    "comments": int(s.get("commentCount", 0)),
                })
            return results
        except Exception:
            return []
