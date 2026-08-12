"""
Генератор сценариев Reels и Stories для ARclinic.
Формат: пошаговая раскадровка с таймингом, текст для подписи, хештеги.
"""

import os
import json
from typing import Optional
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BRAIN = ROOT / "мозг_клиники_ARclinic"


class ReelsScripter:
    """Генератор сценариев для Reels (30-40 сек) и Stories."""

    REEL_STRUCTURE = {
        "hook": {"duration": "0-5 сек", "goal": "Захватить внимание, обозначить тему"},
        "body": {"duration": "5-20 сек", "goal": "Раскрыть тему, показать экспертизу"},
        "visual": {"duration": "20-30 сек", "goal": "Визуальный ряд: процедура, результат, схемы"},
        "cta": {"duration": "30-35 сек", "goal": "Призыв к действию: запись, комментарий, сохранение"},
    }

    def __init__(self):
        self._load_context()

    def _load_context(self):
        tone_path = BRAIN / "голос" / "tone.md"
        principles_path = BRAIN / "идентичность" / "контент-принципы.md"
        self.tone = tone_path.read_text(encoding="utf-8") if tone_path.exists() else ""
        self.principles = principles_path.read_text(encoding="utf-8") if principles_path.exists() else ""

    def generate_reel(
        self,
        topic: str,
        doctor: str,
        duration: str = "0:35",
        rubric: str = "education",
    ) -> str:
        """Генерирует сценарий Reels с раскадровкой."""
        lines = [
            f"### Reels — «{topic}»",
            "",
            f"**Врач:** {doctor}",
            f"**Длительность:** {duration}",
            f"**Рубрика:** {rubric}",
            "",
            "**Сценарий:**",
            "```",
        ]

        total_seconds = self._parse_duration(duration)
        timeline = [
            (0, min(5, total_seconds), "hook"),
            (min(5, total_seconds), min(20, total_seconds), "body"),
            (min(20, total_seconds), min(30, total_seconds), "visual"),
            (min(30, total_seconds), total_seconds, "cta"),
        ]

        for start, end, segment_type in timeline:
            if start >= total_seconds:
                break
            duration_text = f"0:{start:02d}-0:{end:02d}"
            segment = self.REEL_STRUCTURE.get(segment_type, {})
            lines.append(f"[{duration_text}] [{segment.get('goal', '')}]")
            lines.append("[сгенерировать текст]")
            lines.append("")

        lines.append("```")
        lines.append("")
        lines.append("**Текст для подписи:**")
        lines.append("```")
        lines.append("[сгенерировать подпись]")
        lines.append("```")
        lines.append("")
        lines.append("**Хештеги:** #arclinic #арклиникспб [добавить тематические]")

        return "\n".join(lines)

    def generate_story_series(self, topic: str, doctor: str, count: int = 5) -> str:
        """Генерирует серию Stories с таймингом."""
        lines = [
            f"## Stories: «{topic}»",
            f"**Врач:** {doctor}",
            f"**Количество:** {count} слайдов",
            "",
        ]

        story_types = ["hook", "value", "value", "proof", "cta"]
        for i in range(min(count, len(story_types))):
            stype = story_types[i]
            type_descriptions = {
                "hook": "Заголовок, вопрос, интрига — за 1-2 сек принять решение смотреть дальше",
                "value": "Основная ценность: факт, совет, объяснение",
                "proof": "Доказательство: фото до/после, отзыв, результат анализов",
                "cta": "Призыв: записаться, ответить на вопрос, перейти по ссылке",
            }
            lines.append(f"### Слайд {i + 1} ({stype})")
            lines.append(f"**Цель:** {type_descriptions.get(stype, '')}")
            lines.append(f"**Текст:** [сгенерировать]")
            lines.append(f"**Визуал:** [описать: фото врача / процедура / инфографика]")
            lines.append("")

        return "\n".join(lines)

    def _parse_duration(self, duration: str) -> int:
        """Парсит длительность вида '0:35' в секунды."""
        try:
            parts = duration.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except (ValueError, IndexError):
            return 35


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Генератор сценариев Reels/Stories ARclinic")
    parser.add_argument("--topic", required=True, help="Тема Reels")
    parser.add_argument("--doctor", required=True, help="Врач в кадре")
    parser.add_argument("--duration", default="0:35", help="Длительность (М:СС)")
    parser.add_argument("--type", choices=["reel", "story"], default="reel", help="Тип контента")
    parser.add_argument("--rubric", default="education", help="Рубрика")
    parser.add_argument("--story-count", type=int, default=5, help="Кол-во слайдов для Stories")

    args = parser.parse_args()
    scripter = ReelsScripter()

    if args.type == "reel":
        content = scripter.generate_reel(args.topic, args.doctor, args.duration, args.rubric)
    else:
        content = scripter.generate_story_series(args.topic, args.doctor, args.story_count)

    print(content)
