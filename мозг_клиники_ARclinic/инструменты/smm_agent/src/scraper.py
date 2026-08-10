import os
import json
import time
import requests
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Optional
from datetime import datetime
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
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
        })

    def _try_bridge(self, channel: str, max_posts: int) -> List[Dict]:
        bridges = [
            {
                "name": "tg.i-c-a.su",
                "url": f"https://tg.i-c-a.su/json/{channel}?limit={max_posts}",
                "parser": self._parse_icasu_json,
            },
            {
                "name": "rsshub.app",
                "url": f"https://rsshub.app/telegram/channel/{channel}?limit={max_posts}",
                "parser": self._parse_rsshub_atom,
            },
        ]

        for bridge in bridges:
            try:
                resp = self.session.get(bridge["url"], timeout=20)
                if resp.status_code == 200:
                    posts = bridge["parser"](resp, channel, max_posts)
                    if posts:
                        print(f"  [TG] {bridge['name']}: got {len(posts)} posts for @{channel}")
                        return posts
            except Exception:
                continue

        return []

    def _parse_icasu_json(self, resp, channel: str, max_posts: int) -> List[Dict]:
        try:
            data = resp.json()
            messages = data.get("messages", [])
            posts = []
            for msg in messages[:max_posts]:
                msg_id = msg.get("id", "")
                posts.append({
                    "platform": "telegram",
                    "username": channel,
                    "post_id": str(msg_id),
                    "url": f"https://t.me/{channel}/{msg_id}",
                    "caption": (msg.get("message", "") or "")[:500],
                    "timestamp": msg.get("date", ""),
                    "type": "Post",
                    "views": int(msg.get("views", 0) or 0),
                    "reactions": 0,
                    "comments": 0,
                    "forwards": int(msg.get("forwards", 0) or 0),
                    "has_media": bool(msg.get("photo")),
                })
            return posts
        except Exception:
            return []

    def _parse_rsshub_atom(self, resp, channel: str, max_posts: int) -> List[Dict]:
        try:
            content = resp.text
            if "<feed" not in content and "<rss" not in content:
                try:
                    data = resp.json()
                    items = data.get("items", data.get("data", {}).get("items", []))
                    posts = []
                    for item in items[:max_posts]:
                        posts.append({
                            "platform": "telegram",
                            "username": channel,
                            "post_id": item.get("link", "").split("/")[-1] if item.get("link") else "",
                            "url": item.get("link", ""),
                            "caption": (item.get("title", "") or "")[:500],
                            "timestamp": item.get("pubDate", item.get("date", "")),
                            "type": "Post",
                            "views": 0,
                            "reactions": 0,
                            "comments": 0,
                            "forwards": 0,
                        })
                    return posts
                except Exception:
                    return []

            root = ET.fromstring(content)
            ns = {"atom": "http://www.w3.org/2005/Atom", "rss": ""}
            entries = root.findall(".//item") or root.findall(".//atom:entry", ns) or root.findall(".//entry")

            posts = []
            for entry in entries[:max_posts]:
                link = entry.findtext("link", "")
                if not link:
                    link_el = entry.find("link")
                    if link_el is not None:
                        link = link_el.get("href", "")

                title = entry.findtext("title", "")
                pub_date = entry.findtext("pubDate", "") or entry.findtext("published", "") or entry.findtext("updated", "")

                posts.append({
                    "platform": "telegram",
                    "username": channel,
                    "post_id": link.split("/")[-1] if link else "",
                    "url": link or f"https://t.me/{channel}",
                    "caption": (title or "")[:500],
                    "timestamp": pub_date,
                    "type": "Post",
                    "views": 0,
                    "reactions": 0,
                    "comments": 0,
                    "forwards": 0,
                })
            return posts
        except Exception:
            return []

    def fetch_channel_posts(self, channel_username: str, max_posts: int = 50) -> List[Dict]:
        channel = channel_username.lstrip("@")
        print(f"  [TG] Fetching @{channel} (public bridges)")

        posts = self._try_bridge(channel, max_posts)

        if not posts:
            print(f"  [TG] No posts found for @{channel} via public bridges")

        return posts
