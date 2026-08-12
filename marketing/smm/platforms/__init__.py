# Платформенные адаптеры
from .telegram import TelegramAdapter
from .vk import VKAdapter
from .youtube import YouTubeAdapter
from .instagram import InstagramAdapter

__all__ = [
    "TelegramAdapter",
    "VKAdapter",
    "YouTubeAdapter",
    "InstagramAdapter",
]
