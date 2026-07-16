import os
import re
from dotenv import load_dotenv
from src.ai_client import AIClient

load_dotenv()
ai = AIClient()

# 1. Читаем старый контент-план
with open('kp-arclinic.html', 'r', encoding='utf-8') as f:
    old_html = f.read()

# 2. Читаем информацию об Афанасьевой из папки «мозг»
with open('knowledge_base.md', 'r', encoding='utf-8') as f:
    brain = f.read()

# 3. Просим агента найти и заменить ТОЛЬКО пост 26 июня
prompt = f"""
Ты — редактор HTML-кода. Твоя задача — найти в контент-плане пост от 26 июня и заменить его на новый.

ВОТ ВЕСЬ СТАРЫЙ HTML КОД (полный контент-план):
{old_html}

ВОТ ИНФОРМАЦИЯ О ВРАЧЕ АФАНАСЬЕВОЙ ИЗ ПАПКИ «МОЗГ»:
{brain}

ЗАДАНИЕ:
1. Найди в HTML-коде блок, который относится к посту от 26 июня (среда).
2. Удали этот блок полностью.
3. Вставь на его место новый блок с постом про гинеколога-эндокринолога Афанасьеву Лилию Борисовну.
4. НЕ ТРОГАЙ ничего другого — все остальные даты, посты, таблицы, стили должны остаться точно такими же, как в старом коде.

ВЫВЕДИ ПОЛНОСТЬЮ ВЕСЬ ОБНОВЛЁННЫЙ HTML-КОД.
"""

print("🧠 Агент ищет пост от 26 июня...")
response = ai.generate(prompt)

# Сохраняем результат
with open('kp-arclinic-FINAL.html', 'w', encoding='utf-8') as f:
    f.write(response)

print("✅ Готово! Проверь файл kp-arclinic-FINAL.html")