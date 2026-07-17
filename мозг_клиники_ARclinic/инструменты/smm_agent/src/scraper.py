import os
import json
import time
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

APIFY_KEYS = os.getenv("APIFY_KEYS", "").split(",")

ACTORS = {
    "instagram": "nH2AHrwxeTRJoN5hX",
    "tiktok": "GdWCkxBtKWOsKjdch",
}

PLATFORM_NAMES_RU = {
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "vkontakte": "ВКонтакте",
    "youtube": "YouTube",
    "telegram": "Telegram",
}


class ApifyScraper:
    def __init__(self):
        self.keys = [k.strip() for k in APIFY_KEYS if k.strip()]
        self.current_key_index = 0
        self.base_url = "https://api.apify.com/v2"

    @property
    def token(self):
        return self.keys[self.current_key_index] if self.keys else ""

    def _next_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        print(f"  [Apify] Переключение на ключ #{self.current_key_index + 1}")

    def _request(self, method, url, **kwargs):
        for _ in range(len(self.keys)):
            if "params" not in kwargs:
                kwargs["params"] = {}
            kwargs["params"]["token"] = self.token
            resp = requests.request(method, url, **kwargs)
            if resp.status_code == 401:
                print(f"  [Apify] Ключ истёк, пробуем следующий")
                self._next_key()
                continue
            return resp
        raise Exception("Все Apify ключи исчерпаны")

    def fetch_posts(self, platform: str, usernames: List[str], max_posts: int = 50) -> List[Dict]:
        actor_id = ACTORS[platform]

        if platform == "instagram":
            input_data = {
                "username": usernames,
                "resultsLimit": max_posts,
            }
        elif platform == "tiktok":
            input_data = {
                "profiles": usernames,
                "resultsLimit": max_posts,
                "proxyConfig": {"useApifyProxy": True},
            }
        else:
            raise ValueError(f"Unsupported platform: {platform}")

        print(f"  [Apify] Запуск актора {actor_id} для {platform} ({len(usernames)} аккаунтов)")

        resp = self._request("POST", f"{self.base_url}/acts/{actor_id}/runs", json=input_data)
        if resp.status_code == 404:
            raise Exception(f"Actor '{actor_id}' not found")
        resp.raise_for_status()

        run_data = resp.json()
        dataset_id = run_data["data"]["defaultDatasetId"]
        run_id = run_data["data"]["id"]

        status = "RUNNING"
        while status in ("RUNNING", "READY"):
            time.sleep(8)
            s = self._request("GET", f"{self.base_url}/acts/{actor_id}/runs/{run_id}")
            status = s.json()["data"]["status"]
            print(f"  [Apify] Статус: {status}")

        if status != "SUCCEEDED":
            raise Exception(f"Apify run failed: {status}")

        items = self._request("GET", f"{self.base_url}/datasets/{dataset_id}/items")
        result = items.json()
        result = [r for r in result if "error" not in r]
        print(f"  [Apify] Получено {len(result)} постов для {platform}")
        return result

    def normalize_instagram_post(self, raw: Dict, username: str) -> Dict:
        return {
            "platform": "instagram",
            "username": raw.get("ownerUsername", username),
            "post_id": raw.get("shortCode", raw.get("id", "")),
            "url": raw.get("url", ""),
            "caption": (raw.get("caption", "") or "")[:500],
            "timestamp": raw.get("timestamp", ""),
            "type": raw.get("type", "Image"),
            "likes": raw.get("likesCount", 0) or 0,
            "comments": raw.get("commentsCount", 0) or 0,
            "views": raw.get("videoPlayCount", raw.get("videoViewCount", 0)) or 0,
            "is_video": raw.get("type", "") == "Video",
        }

    def normalize_tiktok_post(self, raw: Dict, username: str) -> Dict:
        return {
            "platform": "tiktok",
            "username": username,
            "post_id": raw.get("id", ""),
            "url": raw.get("webVideoUrl", ""),
            "caption": (raw.get("text", "") or "")[:500],
            "timestamp": raw.get("createTimeISO", ""),
            "type": "Video",
            "likes": raw.get("diggCount", 0) or 0,
            "comments": raw.get("commentCount", 0) or 0,
            "views": raw.get("playCount", 0) or 0,
            "shares": raw.get("shareCount", 0) or 0,
        }


class VKScraper:
    def __init__(self, access_token: str):
        self.token = access_token
        self.base_url = "https://api.vk.com/method/"
        self.api_v = "5.199"

    def fetch_posts(self, group_id: str, max_posts: int = 50) -> List[Dict]:
        posts = []
        print(f"  [VK] Запрос постов для {group_id}")

        resp = requests.get(
            f"{self.base_url}wall.get",
            params={
                "domain": group_id,
                "count": min(max_posts, 100),
                "access_token": self.token,
                "v": self.api_v,
            },
        )

        if resp.status_code != 200:
            print(f"  [VK] Ошибка API: {resp.text[:200]}")
            return posts

        data = resp.json()
        if "error" in data:
            print(f"  [VK] API error: {data['error'].get('error_msg', '')}")
            return posts

        items = data.get("response", {}).get("items", [])
        for item in items[:max_posts]:
            posts.append(
                {
                    "platform": "vkontakte",
                    "username": group_id,
                    "post_id": str(item.get("id", "")),
                    "url": f"https://vk.com/wall{item.get('owner_id', 0)}_{item.get('id', '')}",
                    "caption": (item.get("text", "") or "")[:500],
                    "timestamp": str(item.get("date", "")),
                    "type": "Post",
                    "likes": item.get("likes", {}).get("count", 0) or 0,
                    "comments": item.get("comments", {}).get("count", 0) or 0,
                    "views": item.get("views", {}).get("count", 0) or 0,
                    "reposts": item.get("reposts", {}).get("count", 0) or 0,
                }
            )

        print(f"  [VK] Получено {len(posts)} постов для {group_id}")
        return posts


class YouTubeScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3/"

    def fetch_channel_videos(self, channel_id: str, max_videos: int = 50) -> List[Dict]:
        videos = []
        print(f"  [YT] Запрос видео для канала {channel_id}")

        search_resp = requests.get(
            f"{self.base_url}search",
            params={
                "part": "snippet",
                "channelId": channel_id,
                "maxResults": min(max_videos, 50),
                "order": "date",
                "type": "video",
                "key": self.api_key,
            },
        )

        if search_resp.status_code != 200:
            print(f"  [YT] Ошибка search: {search_resp.text[:200]}")
            return videos

        search_data = search_resp.json()
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]

        if not video_ids:
            return videos

        stats_resp = requests.get(
            f"{self.base_url}videos",
            params={
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": self.api_key,
            },
        )

        if stats_resp.status_code != 200:
            print(f"  [YT] Ошибка statistics: {stats_resp.text[:200]}")
            return videos

        stats_data = stats_resp.json()
        stats_map = {
            item["id"]: item.get("statistics", {})
            for item in stats_data.get("items", [])
        }

        for item in search_data.get("items", [])[:max_videos]:
            vid = item["id"]["videoId"]
            snip = item["snippet"]
            stats = stats_map.get(vid, {})

            videos.append(
                {
                    "platform": "youtube",
                    "username": channel_id,
                    "post_id": vid,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "caption": (snip.get("title", "") or "")[:500],
                    "timestamp": snip.get("publishedAt", ""),
                    "type": "Video",
                    "likes": int(stats.get("likeCount", 0) or 0),
                    "comments": int(stats.get("commentCount", 0) or 0),
                    "views": int(stats.get("viewCount", 0) or 0),
                }
            )

        print(f"  [YT] Получено {len(videos)} видео для {channel_id}")
        return videos


class TelegramScraper:
    """
    Парсер Telegram через публичные данные.
    Для каналов используем tgstat.ru или telemetr.me через парсинг HTML.
    Для приватных каналов/чатов нужен Telethon с сессией.
    """

    def __init__(self):
        pass

    def fetch_channel_posts(self, channel_username: str, max_posts: int = 50) -> List[Dict]:
        posts = []
        print(f"  [TG] Запрос постов для @{channel_username} (через tgstat)")

        try:
            url = f"https://tgstat.ru/channel/@{channel_username}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=30)

            if resp.status_code != 200:
                print(f"  [TG] Не удалось получить данные: HTTP {resp.status_code}")
                return posts

            from html.parser import HTMLParser

            class TGStatParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.posts = []
                    self.in_post = False
                    self.in_views = False
                    self.current = {}
                    self.data_collect = ""

                def handle_starttag(self, tag, attrs):
                    attrs_dict = dict(attrs)
                    cls = attrs_dict.get("class", "")
                    if "post" in cls.lower() or "article" in cls.lower():
                        self.in_post = True
                        self.current = {}
                    if self.in_post and "views" in cls.lower():
                        self.in_views = True

                def handle_endtag(self, tag):
                    if self.in_post and tag in ("div", "article"):
                        if self.current:
                            self.posts.append(self.current)
                        self.in_post = False

                def handle_data(self, data):
                    if self.in_views:
                        self.current["views_raw"] = data.strip()

            parser = TGStatParser()
            parser.feed(resp.text)

            print(f"  [TG] Найдено {len(posts)} постов в HTML (@{channel_username})")

        except Exception as e:
            print(f"  [TG] Ошибка парсинга @{channel_username}: {e}")

        return posts
