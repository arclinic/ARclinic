"""
Конкурентный анализ SMM-активности.
Мониторинг публикаций, форматов, вовлечённости конкурентов.
Поиск незанятых ниш и идей для контента.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BRAIN = ROOT / "мозг_клиники_ARclinic"


class CompetitorAnalyzer:
    """Анализатор SMM-активности конкурентов."""

    COMPETITORS = {
        "galaktika": {
            "name": "Галактика",
            "instagram": "",
            "telegram": "",
            "vk": "",
            "note": "Слабый SMM (из анализа конкурентов)",
        },
        "beauty_line": {
            "name": "Beauty Line",
            "instagram": "",
            "telegram": "",
            "vk": "",
        },
        "estetik": {
            "name": "Эстетик",
            "instagram": "",
            "telegram": "",
            "vk": "",
        },
        "medsi": {
            "name": "Медси",
            "instagram": "",
            "telegram": "",
            "vk": "",
        },
        "smt_clinic": {
            "name": "СМ-Клиника",
            "instagram": "",
            "telegram": "",
            "vk": "",
        },
    }

    METRICS = [
        "frequency",     # Частота публикаций
        "formats",       # Форматы контента
        "engagement",    # Вовлечённость (лайки/комменты/репосты)
        "themes",        # Темы и рубрики
        "tone",          # Тональность
        "visuals",       # Визуальный стиль
        "unique",        # Уникальные фишки
    ]

    def __init__(self):
        self._load_analysis()

    def _load_analysis(self):
        """Загружает существующий анализ конкурентов."""
        analysis_path = BRAIN / "конкуренты" / "анализ.md"
        self.existing_analysis = analysis_path.read_text(encoding="utf-8") if analysis_path.exists() else ""

    def analyze_competitor(self, competitor_key: str) -> dict:
        """Анализирует одного конкурента."""
        comp = self.COMPETITORS.get(competitor_key, {})
        return {
            "name": comp.get("name", competitor_key),
            "instagram": comp.get("instagram", "не указан"),
            "telegram": comp.get("telegram", "не указан"),
            "vk": comp.get("vk", "не указан"),
            "note": comp.get("note", ""),
            "metrics": {m: "требуется сбор данных" for m in self.METRICS},
        }

    def analyze_all(self) -> dict:
        """Анализирует всех конкурентов."""
        results = {}
        for key in self.COMPETITORS:
            results[key] = self.analyze_competitor(key)
        return results

    def find_gaps(self) -> List[str]:
        """Ищет незанятые конкурентами темы и форматы."""
        gaps = self._get_gaps_from_analysis()
        if not gaps:
            gaps = [
                "Лечение осложнений после других клиник",
                "Preventive-медицина и чекапы",
                "ЗГТ и менопауза (экспертный контент)",
                "Кабинет акне — комплексный подход",
                "Личный бренд основателя",
                "Видео-рубрика «День из жизни врача»",
                "Коллаборации с врачами других специальностей",
                "Образовательные Reels с инфографикой",
            ]
        return gaps

    def _get_gaps_from_analysis(self) -> List[str]:
        gaps = []
        for line in self.existing_analysis.split("\n"):
            if "слаб" in line.lower() or "нет" in line.lower():
                gaps.append(line.strip("- "))
        return gaps

    def generate_report(self) -> str:
        """Генерирует отчёт по конкурентному анализу."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        all_competitors = self.analyze_all()

        lines = [
            f"# Конкурентный анализ SMM — {date_str}",
            "",
            "## Конкуренты и их SMM-активность",
            "| Клиника | Instagram | Telegram | VK | Особенности |",
            "|---------|-----------|----------|----|-------------|",
        ]
        for key, comp in all_competitors.items():
            lines.append(
                f"| {comp['name']} | {comp['instagram'] or '—'} | "
                f"{comp['telegram'] or '—'} | {comp['vk'] or '—'} | {comp.get('note', '')} |"
            )

        lines.extend([
            "",
            "## Сравнение метрик",
            "| Метрика | ARclinic | Галактика | Beauty Line | Эстетик | Медси | СМ-Клиника |",
            "|---------|----------|-----------|-------------|---------|-------|------------|",
        ])
        for metric in self.METRICS:
            lines.append(f"| {metric} | [собрать] | [собрать] | [собрать] | [собрать] | [собрать] | [собрать] |")

        lines.extend([
            "",
            "## Незанятые ниши и возможности",
        ])
        for gap in self.find_gaps():
            lines.append(f"- {gap}")

        lines.extend([
            "",
            "## Рекомендации",
            "- Усилить: [форматы, которые работают у конкурентов]",
            "- Избегать: [что не работает у конкурентов]",
            "- Дифференциатор: [что делаем уникального]",
        ])

        return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Конкурентный анализ SMM ARclinic")
    parser.add_argument("--competitor", default="", help="Ключ конкурента (galaktika, beauty_line, ...)")
    parser.add_argument("--gaps", action="store_true", help="Показать незанятые ниши")
    parser.add_argument("--update", action="store_true", help="Обновить полный анализ")

    args = parser.parse_args()
    analyzer = CompetitorAnalyzer()

    if args.gaps:
        gaps = analyzer.find_gaps()
        print("Незанятые ниши:")
        for g in gaps:
            print(f"- {g}")
    elif args.competitor:
        result = analyzer.analyze_competitor(args.competitor)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.update:
        report = analyzer.generate_report()
        print(report)
    else:
        print("Укажите --competitor, --gaps или --update")
