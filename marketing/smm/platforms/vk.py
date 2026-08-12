"""
Адаптер VK: API для публикации в группу/канал.
"""

import os
import json
import requests
from typing import Optional, Dict, Any


class VKAdapter:
    """Работа с VK API."""

    API_VERSION = "5.199"

    def __init__(self, access_token: str = "", group_id: str = ""):
        self.token = access_token or os.getenv("VK_ACCESS_TOKEN", "")
        self.group_id = group_id or os.getenv("VK_GROUP_ID", "")

    def _api(self, method: str, **params) -> dict:
        """Вызов метода VK API."""
        params.setdefault("v", self.API_VERSION)
        params.setdefault("access_token", self.token)
        url = f"https://api.vk.com/method/{method}"
        resp = requests.get(url, params=params, timeout=15)
        return resp.json()

    def wall_post(self, message: str, attachments: str = "",
                  from_group: bool = True) -> dict:
        """Публикация поста на стене группы."""
        return self._api("wall.post", owner_id=f"-{self.group_id}",
                         from_group=int(from_group), message=message,
                         attachments=attachments)

    def wall_get(self, count: int = 10, offset: int = 0) -> dict:
        """Получение последних постов."""
        return self._api("wall.get", owner_id=f"-{self.group_id}",
                         count=count, offset=offset)

    def wall_edit(self, post_id: int, message: str,
                  attachments: str = "") -> dict:
        """Редактирование поста."""
        return self._api("wall.edit", owner_id=f"-{self.group_id}",
                         post_id=post_id, message=message, attachments=attachments)

    def wall_delete(self, post_id: int) -> dict:
        """Удаление поста."""
        return self._api("wall.delete", owner_id=f"-{self.group_id}",
                         post_id=post_id)

    def upload_photo(self, photo_path: str) -> dict:
        """Загрузка фото на стену."""
        server = self._api("photos.getWallUploadServer",
                           group_id=self.group_id)
        if "error" in server:
            return server

        upload_url = server["response"]["upload_url"]
        with open(photo_path, "rb") as photo:
            upload = requests.post(upload_url, files={"photo": photo},
                                   timeout=30).json()

        save = self._api("photos.saveWallPhoto", group_id=self.group_id,
                         photo=upload["photo"], server=upload["server"],
                         hash=upload["hash"])
        if "response" in save and save["response"]:
            photo_data = save["response"][0]
            return {
                "id": photo_data["id"],
                "owner_id": photo_data["owner_id"],
                "attachment": f"photo{photo_data['owner_id']}_{photo_data['id']}",
            }
        return {"error": "saveWallPhoto failed"}

    def get_group_info(self) -> dict:
        """Информация о группе."""
        return self._api("groups.getById", group_id=self.group_id)

    def get_members_count(self) -> int:
        """Количество подписчиков."""
        resp = self._api("groups.getMembers", group_id=self.group_id)
        if "response" in resp:
            return resp["response"].get("count", 0)
        return 0
