"""
Адаптер Instagram: контент-подготовка для публикации.
Прямой автопостинг недоступен через бесплатные API Meta.
Используется для: генерации подписей, хештегов, подготовки медиа.
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
BRAIN = ROOT / "мозг_клиники_ARclinic"


class InstagramAdapter:
    """Подготовка контента для Instagram (без автопостинга)."""

    HASHTAG_GROUPS = {
        "clinic": ["#arclinic", "#арклиникспб"],
        "cosmetology": ["#косметологияспб", "#косметологспб", "#омоложение"],
        "injections": ["#ботоксспб", "#филлерыспб", "#контурнаяпластика"],
        "laser": ["#лазернаякосметология", "#лазерспб"],
        "acne": ["#акне", "#лечениеакне", "#чистаякожа"],
        "gynecology": ["#гинекологияспб", "#женскоездоровье", "#згт"],
        "neurology": ["#неврологспб", "#мигрень"],
        "lip": ["#губы", "#увеличениегубспб"],
        "peeling": ["#пилингспб", "#чисткалица"],
        "rflifting": ["#рфлифтинг", "#лифтинглица"],
    }

    POST_TEMPLATE = """{text}

{hashtags}"""

    REEL_TEMPLATE = """{text}

{hashtags}"""

    def __init__(self):
        pass

    def generate_hashtags(self, topic: str, count: int = 5) -> str:
        """Генерирует хештеги по теме."""
        tags = ["#arclinic", "#арклиникспб"]

        topic_lower = topic.lower()
        for group_key, group_tags in self.HASHTAG_GROUPS.items():
            if group_key in topic_lower:
                tags.extend(group_tags[:max(0, count - len(tags))])
                break

        tags = list(dict.fromkeys(tags))
        if len(tags) > count + 2:
            tags = tags[:count + 2]

        return " ".join(tags)

    def prepare_post(self, text: str, topic: str = "",
                     format_type: str = "post") -> dict:
        """Подготавливает пост для публикации в Instagram."""
        hashtags = self.generate_hashtags(topic)

        final_text = text
        if "#arclinic" not in text.lower():
            final_text += f"\n\n{hashtags}"

        sections = []
        if len(final_text) > 2000:
            lines = final_text.split("\n")
            current = ""
            for line in lines:
                if len(current) + len(line) + 1 > 2000:
                    sections.append(current.strip())
                    current = line
                else:
                    current += ("\n" if current else "") + line
            if current:
                sections.append(current.strip())
        else:
            sections = [final_text]

        return {
            "text": final_text,
            "sections": sections if len(sections) > 1 else None,
            "hashtags": hashtags,
            "char_count": len(final_text),
            "note": "Instagram не поддерживает прямой автопостинг через бесплатные API. "
                    "Опубликуйте через Meta Business Suite, Buffer или вручную.",
        }

    def prepare_carousel(self, slides: List[str], topic: str = "") -> dict:
        """Подготавливает карусель."""
        return {
            "slides": [self.prepare_post(s, topic, "carousel") for s in slides],
            "total_slides": len(slides),
            "note": "Карусель подготовлена. Загрузите слайды через приложение Instagram или Meta Business Suite.",
        }

    def prepare_reel(self, text: str, topic: str = "",
                     duration_sec: int = 35) -> dict:
        """Подготавливает Reels для публикации."""
        hashtags = self.generate_hashtags(topic)
        final_text = text if "#arclinic" in text.lower() else f"{text}\n\n{hashtags}"

        return {
            "text": final_text,
            "caption": final_text[:2200],
            "hashtags": hashtags,
            "duration": duration_sec,
            "char_count": len(final_text),
            "note": "Reels подготовлен. Загрузите видео и текст через приложение Instagram.",
        }
