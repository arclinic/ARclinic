"""
Генератор текстовых постов для соцсетей ARclinic.
Форматы: карусель, одиночный пост, лонгрид.
Адаптация под платформы: Instagram, Telegram, VK.
"""

import os
from typing import Optional
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BRAIN = ROOT / "мозг_клиники_ARclinic"


class PostWriter:
    """Писатель постов для Instagram, Telegram, VK."""

    POST_TYPES = {
        "before_after": "До/После — фото/карусель с результатом процедуры",
        "educational": "Образовательный — разбор мифа, объяснение процесса, чек-лист",
        "faq": "FAQ — ответы на частые вопросы пациентов",
        "case_study": "Кейс — разбор сложного случая из практики",
        "behind_scenes": "Закулисье — как работает клиника, стандарты, процессы",
        "lifestyle": "Лайфстайл — день врача, хобби, личные истории",
        "promo": "Промо-пост — акция, скидка, специальное предложение",
    }

    PLATFORM_LIMITS = {
        "instagram": {"max_chars": 2200, "max_hashtags": 30, "emoji": True, "line_breaks": True},
        "telegram": {"max_chars": 4096, "max_hashtags": 10, "emoji": True, "line_breaks": True},
        "vk": {"max_chars": 16384, "max_hashtags": 10, "emoji": True, "line_breaks": True},
        "youtube": {"max_chars": 5000, "max_hashtags": 15, "emoji": False, "line_breaks": True},
        "dzen": {"max_chars": 100000, "max_hashtags": 0, "emoji": False, "line_breaks": True},
    }

    def __init__(self):
        self._load_context()

    def _load_context(self):
        tone_path = BRAIN / "голос" / "tone.md"
        principles_path = BRAIN / "идентичность" / "контент-принципы.md"
        self.tone = tone_path.read_text(encoding="utf-8") if tone_path.exists() else ""
        self.principles = principles_path.read_text(encoding="utf-8") if principles_path.exists() else ""

    def generate_post(
        self,
        post_type: str,
        topic: str,
        doctor: str = "",
        platform: str = "instagram",
    ) -> str:
        """Генерирует пост с адаптацией под платформу."""
        limits = self.PLATFORM_LIMITS.get(platform, self.PLATFORM_LIMITS["instagram"])
        post_info = self.POST_TYPES.get(post_type, self.POST_TYPES["educational"])

        lines = [
            f"## Пост для {platform.upper()}",
            f"**Тип:** {post_type} — {post_info}",
            f"**Тема:** {topic}",
        ]
        if doctor:
            lines.append(f"**Врач:** {doctor}")
        lines.extend([
            f"**Макс. символов:** {limits['max_chars']}",
            "",
            "**Текст поста:**",
            "```",
            "[сгенерировать текст в голосе Анны: экспертно, тепло, без воды]",
            "```",
        ])

        if post_type in ("before_after", "faq", "educational"):
            lines.extend([
                "",
                "**Сценарий карусели:**",
                "```",
                "Слайд 1: [заголовок/обложка]",
                "Слайд 2: [контент]",
                "Слайд 3: [контент]",
                "Слайд N: [CTA — запись, ссылка]",
                "```",
            ])

        lines.extend([
            "",
            "**Хештеги:** #arclinic #арклиникспб [добавить 3-5 тематических]",
        ])

        return "\n".join(lines)

    def generate_carousel(self, topic: str, doctor: str, slides: int = 5) -> str:
        """Генерирует структуру карусели для Instagram."""
        lines = [
            f"## Карусель: «{topic}»",
            f"**Врач:** {doctor}",
            f"**Слайдов:** {slides}",
            "",
        ]

        slide_purposes = {
            1: ("Обложка", "Заголовок, привлекающий внимание"),
            2: ("Проблема", "Описание боли/ситуации, с которой сталкивается пациент"),
        }
        for i in range(3, slides):
            slide_purposes[i] = ("Контент", "Факт / совет / доказательство")
        slide_purposes[slides] = ("CTA", "Призыв к действию: запись, комментарий, сохранение")

        for i in range(1, slides + 1):
            purpose, desc = slide_purposes.get(i, ("Контент", ""))
            lines.append(f"**Слайд {i}** ({purpose})")
            lines.append(f"> {desc}")
            lines.append(f"> Визуал: [описать: фото / инфографика / текст на фоне]")
            lines.append("")

        lines.append("**Текст для подписи:**")
        lines.append("```")
        lines.append("[сгенерировать]")
        lines.append("```")
        return "\n".join(lines)

    def adapt_for_platform(self, text: str, platform: str) -> str:
        """Адаптирует текст под ограничения платформы."""
        limits = self.PLATFORM_LIMITS.get(platform, self.PLATFORM_LIMITS["instagram"])
        if len(text) > limits["max_chars"]:
            text = text[: limits["max_chars"] - 3] + "..."
        return text


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Генератор постов ARclinic")
    parser.add_argument("--type", choices=list(PostWriter.POST_TYPES.keys()), default="educational",
                        help="Тип поста")
    parser.add_argument("--topic", required=True, help="Тема поста")
    parser.add_argument("--doctor", default="", help="Врач")
    parser.add_argument("--platform", choices=["instagram", "telegram", "vk", "youtube", "dzen"],
                        default="instagram", help="Платформа")

    args = parser.parse_args()
    writer = PostWriter()
    content = writer.generate_post(args.type, args.topic, args.doctor, args.platform)
    print(content)

    if args.type in ("before_after", "faq"):
        print("\n" + "=" * 60 + "\n")
        carousel = writer.generate_carousel(args.topic, args.doctor)
        print(carousel)
