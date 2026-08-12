"""
Копирайтер ARclinic: продающие и экспертные тексты голосом Анны.
Форматы: лендинги, промо, рассылки, скрипты общения, UTM-разметка.
"""

import os
from typing import Optional
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BRAIN = ROOT / "мозг_клиники_ARclinic"


class Copywriter:
    """Копирайтер для ARclinic. Пишет голосом Анны."""

    COPY_TYPES = {
        "landing": {
            "name": "Лендинг",
            "sections": ["hero", "problem", "solution", "us_advantage", "doctors", "how_it_works",
                         "before_after", "reviews", "cta_block", "faq"],
        },
        "promo": {
            "name": "Промо-кампания",
            "sections": ["hook", "offer", "what_included", "why_us", "cost", "cta"],
        },
        "email_sequence": {
            "name": "Email-последовательность",
            "sections": ["welcome", "value_1", "value_2", "case", "objections", "final_cta"],
        },
        "messenger_onboarding": {
            "name": "Онбординг в мессенджере",
            "sections": ["greeting", "diagnosis", "expectations", "first_step"],
        },
        "messenger_retention": {
            "name": "Удержание в мессенджере",
            "sections": ["check_in", "reminder", "promo", "thanks"],
        },
        "messenger_reactivation": {
            "name": "Реактивация в мессенджере",
            "sections": ["miss_you", "new_offer", "cta"],
        },
        "expert_article": {
            "name": "Экспертная статья",
            "sections": ["intro", "myth_vs_reality", "mechanism", "who_needs", "risks", "conclusion"],
        },
        "service_card": {
            "name": "Карточка услуги",
            "sections": ["name", "short_description", "how_it_works", "result", "doctors", "price_from", "cta"],
        },
    }

    UTMS = {
        "source": {"instagram": "instagram", "telegram": "telegram", "vk": "vk", "yandex": "yandex"},
        "medium": {"post": "social_post", "story": "social_story", "reel": "social_reel",
                   "ad": "cpc", "email": "email", "messenger": "messenger"},
        "campaign": {"new_year": "ny2026", "summer": "summer2026", "autumn": "autumn2026",
                     "checkup": "checkup", "acne": "acne_cabinet", "zgt": "zgt"},
    }

    def __init__(self):
        self._load_context()

    def _load_context(self):
        tone_path = BRAIN / "голос" / "tone.md"
        principles_path = BRAIN / "идентичность" / "контент-принципы.md"
        clinic_path = BRAIN / "бизнес" / "клиника.md"
        objections_path = BRAIN / "бизнес" / "возражения.md"
        audience_path = BRAIN / "бизнес" / "аудитория.md"
        self.tone = tone_path.read_text(encoding="utf-8") if tone_path.exists() else ""
        self.principles = principles_path.read_text(encoding="utf-8") if principles_path.exists() else ""
        self.clinic = clinic_path.read_text(encoding="utf-8") if clinic_path.exists() else ""
        self.objections = objections_path.read_text(encoding="utf-8") if objections_path.exists() else ""
        self.audience = audience_path.read_text(encoding="utf-8") if audience_path.exists() else ""

    def generate_copy(self, copy_type: str, topic: str, service: str = "", audience_segment: str = "") -> str:
        """Генерирует структуру текста."""
        info = self.COPY_TYPES.get(copy_type, self.COPY_TYPES["promo"])
        lines = [
            f"# {info['name']}: «{topic}»",
            f"**Голос:** Анны Резник (экспертный, тёплый, уверенный)",
        ]
        if service:
            lines.append(f"**Услуга:** {service}")
        if audience_segment:
            lines.append(f"**Сегмент аудитории:** {audience_segment}")
        lines.append("")

        for section in info["sections"]:
            section_names = {
                "hero": "Главный экран (заголовок + подзаголовок)",
                "problem": "Проблема / боль клиента",
                "solution": "Решение (услуга/процедура)",
                "us_advantage": "Наше преимущество / почему ARclinic",
                "doctors": "Врачи / эксперты",
                "how_it_works": "Как проходит процедура / этапы",
                "before_after": "Результаты до/после",
                "reviews": "Отзывы пациентов",
                "cta_block": "Призыв к действию",
                "faq": "Вопросы и ответы",
                "hook": "Заголовок-крючок",
                "offer": "Предложение (что, кому, зачем)",
                "what_included": "Что входит",
                "why_us": "Почему мы, а не конкуренты",
                "cost": "Стоимость / акция",
                "cta": "Призыв к действию",
                "welcome": "Приветственное письмо",
                "value_1": "Ценность 1: экспертность",
                "value_2": "Ценность 2: кейс/результат",
                "case": "Разбор кейса",
                "objections": "Работа с возражениями",
                "final_cta": "Финальный призыв",
                "greeting": "Приветствие и знакомство",
                "diagnosis": "Диагностика потребностей",
                "expectations": "Установка ожиданий",
                "first_step": "Первый шаг (запись)",
                "check_in": "Check-in после приёма",
                "reminder": "Напоминание о процедуре",
                "promo": "Спецпредложение / акция",
                "thanks": "Благодарность и приглашение вернуться",
                "miss_you": "Соскучились — напоминание о клинике",
                "new_offer": "Новое предложение",
                "intro": "Введение: почему это важно",
                "myth_vs_reality": "Миф vs реальность",
                "mechanism": "Как это работает (научно, но доступно)",
                "who_needs": "Кому это нужно / показания",
                "risks": "Риски и противопоказания",
                "conclusion": "Заключение: резюме + CTA",
                "name": "Название услуги",
                "short_description": "Краткое описание (1-2 предложения)",
                "result": "Какой результат получает пациент",
                "price_from": "Цена от ...",
            }
            lines.append(f"## {section_names.get(section, section)}")
            lines.append("[сгенерировать текст]")
            lines.append("")

        return "\n".join(lines)

    def generate_utm(self, source: str, medium: str, campaign: str, content: str = "",
                     term: str = "") -> str:
        """Генерирует UTM-метку."""
        utm_parts = [
            f"utm_source={self.UTMS['source'].get(source, source)}",
            f"utm_medium={self.UTMS['medium'].get(medium, medium)}",
            f"utm_campaign={self.UTMS['campaign'].get(campaign, campaign)}",
        ]
        if content:
            utm_parts.append(f"utm_content={content}")
        if term:
            utm_parts.append(f"utm_term={term}")
        return "?" + "&".join(utm_parts)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Копирайтер ARclinic")
    parser.add_argument("--type", choices=list(Copywriter.COPY_TYPES.keys()), default="promo",
                        help="Тип текста")
    parser.add_argument("--topic", default="", help="Тема")
    parser.add_argument("--service", default="", help="Услуга")
    parser.add_argument("--segment", default="", help="Сегмент аудитории")
    parser.add_argument("--utm-source", default="instagram", help="Источник UTM")
    parser.add_argument("--utm-medium", default="post", help="Канал UTM")
    parser.add_argument("--utm-campaign", default="", help="Кампания UTM")

    args = parser.parse_args()
    cw = Copywriter()
    content = cw.generate_copy(args.type, args.topic or args.type, args.service, args.segment)
    print(content)

    if args.utm_campaign:
        utm = cw.generate_utm(args.utm_source, args.utm_medium, args.utm_campaign)
        print(f"\nUTM-метка: {utm}")
