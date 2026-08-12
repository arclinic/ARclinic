"""
Адаптер Telegram: Bot API для публикации постов, фото, видео.
"""

import os
import json
import requests
from typing import Optional, Dict, Any


class TelegramAdapter:
    """Работа с Telegram Bot API."""

    def __init__(self, bot_token: str = "", channel_id: str = ""):
        self.token = bot_token or os.getenv("TG_BOT_TOKEN", "")
        self.channel_id = channel_id or os.getenv("TG_CHANNEL_ID", "")

    def _api(self, method: str, **kwargs) -> dict:
        """Вызов метода Telegram Bot API."""
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        resp = requests.post(url, data=kwargs, timeout=30)
        return resp.json()

    def send_message(self, text: str, parse_mode: str = "HTML",
                     disable_notification: bool = False) -> dict:
        return self._api("sendMessage", chat_id=self.channel_id, text=text,
                         parse_mode=parse_mode, disable_notification=disable_notification,
                         disable_web_page_preview=True)

    def send_photo(self, photo_path: str, caption: str = "",
                   parse_mode: str = "HTML") -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        with open(photo_path, "rb") as photo:
            return requests.post(url, data={
                "chat_id": self.channel_id, "caption": caption, "parse_mode": parse_mode,
            }, files={"photo": photo}, timeout=30).json()

    def send_video(self, video_path: str, caption: str = "",
                   parse_mode: str = "HTML") -> dict:
        url = f"https://api.telegram.org/bot{self.token}/sendVideo"
        with open(video_path, "rb") as video:
            return requests.post(url, data={
                "chat_id": self.channel_id, "caption": caption, "parse_mode": parse_mode,
            }, files={"video": video}, timeout=60).json()

    def send_poll(self, question: str, options: list,
                  is_anonymous: bool = True) -> dict:
        return self._api("sendPoll", chat_id=self.channel_id, question=question,
                         options=json.dumps(options), is_anonymous=is_anonymous)

    def edit_message(self, message_id: int, text: str,
                     parse_mode: str = "HTML") -> dict:
        return self._api("editMessageText", chat_id=self.channel_id,
                         message_id=message_id, text=text, parse_mode=parse_mode)

    def delete_message(self, message_id: int) -> dict:
        return self._api("deleteMessage", chat_id=self.channel_id,
                         message_id=message_id)

    def pin_message(self, message_id: int) -> dict:
        return self._api("pinChatMessage", chat_id=self.channel_id,
                         message_id=message_id)

    def get_chat_info(self) -> dict:
        return self._api("getChat", chat_id=self.channel_id)
