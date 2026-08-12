"""
Автопостинг в соцсети ARclinic.
Поддерживает: Telegram (Bot API), VK (API).
Instagram — только контент-подготовка (ограничения Meta API).
YouTube — информация о видео (Data API).

Telegram-каналы — настройка через реестр smm/channels.py.
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from channels import get_channel, get_channel_id, list_channels, DEFAULT_CHANNEL


class AutoPoster:
    """Автопостинг в Telegram и VK."""

    def __init__(self, channel_key: str = ""):
        self.channel_key = channel_key or DEFAULT_CHANNEL
        self.tg_token = os.getenv("TG_BOT_TOKEN", "")
        self.tg_channel = get_channel_id(self.channel_key)
        self.vk_token = os.getenv("VK_ACCESS_TOKEN", "")
        self.vk_group_id = os.getenv("VK_GROUP_ID", "")
        self.content_dir = ROOT / "marketing" / "content_queue"
        self.content_dir.mkdir(parents=True, exist_ok=True)

    def post_to_telegram(
        self,
        text: str,
        photo_path: str = "",
        video_path: str = "",
        parse_mode: str = "HTML",
        disable_notification: bool = False,
        channel_key: str = "",
    ) -> dict:
        """Публикует пост в Telegram-канал через Bot API."""
        if not self.tg_token:
            return {"error": "TG_BOT_TOKEN не задан в .env"}

        chat_id = get_channel_id(channel_key) if channel_key else self.tg_channel
        if not chat_id:
            return {"error": f"ID канала не задан в .env (channel={channel_key or self.channel_key})"}

        try:
            if photo_path and os.path.exists(photo_path):
                url = f"https://api.telegram.org/bot{self.tg_token}/sendPhoto"
                with open(photo_path, "rb") as photo:
                    files = {"photo": photo}
                    data = {
                        "chat_id": chat_id,
                        "caption": text,
                        "parse_mode": parse_mode,
                        "disable_notification": disable_notification,
                    }
                    resp = requests.post(url, data=data, files=files, timeout=30)
            elif video_path and os.path.exists(video_path):
                url = f"https://api.telegram.org/bot{self.tg_token}/sendVideo"
                with open(video_path, "rb") as video:
                    files = {"video": video}
                    data = {
                        "chat_id": chat_id,
                        "caption": text,
                        "parse_mode": parse_mode,
                        "disable_notification": disable_notification,
                    }
                    resp = requests.post(url, data=data, files=files, timeout=60)
            else:
                url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_notification": disable_notification,
                    "disable_web_page_preview": True,
                }
                resp = requests.post(url, data=data, timeout=15)

            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def post_to_vk(
        self,
        text: str,
        photo_path: str = "",
        video_path: str = "",
        from_group: bool = True,
    ) -> dict:
        """Публикует пост в VK-группу через VK API."""
        if not self.vk_token:
            return {"error": "VK_ACCESS_TOKEN не задан в .env"}
        if not self.vk_group_id:
            return {"error": "VK_GROUP_ID не задан в .env"}

        try:
            attachments = []
            owner_id = f"-{self.vk_group_id}"

            if photo_path and os.path.exists(photo_path):
                photo_result = self._vk_upload_photo(photo_path)
                if photo_result and "error" not in photo_result:
                    attachments.append(
                        f"photo{photo_result.get('owner_id')}_{photo_result.get('id')}"
                    )

            if video_path and os.path.exists(video_path):
                video_result = self._vk_upload_video(video_path)
                if video_result and "error" not in video_result:
                    attachments.append(
                        f"video{video_result.get('owner_id')}_{video_result.get('video_id')}"
                    )

            url = "https://api.vk.com/method/wall.post"
            params = {
                "owner_id": owner_id,
                "from_group": int(from_group),
                "message": text,
                "attachments": ",".join(attachments) if attachments else "",
                "v": "5.199",
                "access_token": self.vk_token,
            }
            resp = requests.get(url, params=params, timeout=15)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def _vk_upload_photo(self, photo_path: str) -> dict:
        """Загружает фото на сервер VK для поста."""
        try:
            save_url = "https://api.vk.com/method/photos.getWallUploadServer"
            params = {
                "group_id": self.vk_group_id,
                "v": "5.199",
                "access_token": self.vk_token,
            }
            server_resp = requests.get(save_url, params=params, timeout=15).json()
            if "error" in server_resp:
                return server_resp

            upload_url = server_resp["response"]["upload_url"]
            with open(photo_path, "rb") as photo:
                upload_resp = requests.post(upload_url, files={"photo": photo}, timeout=30).json()

            save_params = {
                "group_id": self.vk_group_id,
                "photo": upload_resp["photo"],
                "server": upload_resp["server"],
                "hash": upload_resp["hash"],
                "v": "5.199",
                "access_token": self.vk_token,
            }
            save_resp = requests.get(
                "https://api.vk.com/method/photos.saveWallPhoto",
                params=save_params,
                timeout=15,
            ).json()

            if "response" in save_resp and save_resp["response"]:
                return save_resp["response"][0]
            return {"error": "saveWallPhoto failed"}
        except Exception as e:
            return {"error": str(e)}

    def _vk_upload_video(self, video_path: str) -> dict:
        """Загружает видео на сервер VK."""
        try:
            save_url = "https://api.vk.com/method/video.save"
            params = {
                "group_id": self.vk_group_id,
                "name": os.path.basename(video_path),
                "v": "5.199",
                "access_token": self.vk_token,
            }
            save_resp = requests.get(save_url, params=params, timeout=15).json()
            if "error" in save_resp:
                return save_resp

            upload_url = save_resp["response"]["upload_url"]
            video_id = save_resp["response"]["video_id"]
            owner_id = save_resp["response"]["owner_id"]

            with open(video_path, "rb") as video:
                requests.post(upload_url, files={"video_file": video}, timeout=120)

            return {"owner_id": owner_id, "video_id": video_id}
        except Exception as e:
            return {"error": str(e)}

    def schedule_post(
        self,
        platform: str,
        text: str,
        photo_path: str = "",
        video_path: str = "",
        publish_at: str = "",
    ) -> dict:
        """Планирует пост на будущее."""
        if not publish_at:
            return self.post_to_telegram(text, photo_path, video_path)

        task = {
            "platform": platform,
            "text": text,
            "photo_path": photo_path,
            "video_path": video_path,
            "publish_at": publish_at,
            "status": "scheduled",
        }
        task_file = self.content_dir / f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task, f, ensure_ascii=False, indent=2)

        return {"status": "scheduled", "file": str(task_file), "publish_at": publish_at}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    import argparse
    parser = argparse.ArgumentParser(description="Автопостинг ARclinic")
    parser.add_argument("--platform", choices=["telegram", "vk"], required=True,
                        help="Платформа")
    parser.add_argument("--channel", default="",
                        choices=[""] + list_channels(),
                        help="Telegram-канал (arclinic или ginekolog, по умолчанию arclinic)")
    parser.add_argument("--text", required=True, help="Текст поста")
    parser.add_argument("--photo", default="", help="Путь к фото")
    parser.add_argument("--video", default="", help="Путь к видео")
    parser.add_argument("--schedule", default="", help="Запланировать на (ISO-формат)")
    parser.add_argument("--silent", action="store_true", help="Без уведомления")

    args = parser.parse_args()
    poster = AutoPoster(channel_key=args.channel)

    if args.platform == "telegram":
        result = poster.post_to_telegram(
            args.text, args.photo, args.video,
            disable_notification=args.silent,
        )
    else:
        result = poster.post_to_vk(args.text, args.photo, args.video)

    print(json.dumps(result, ensure_ascii=False, indent=2))
