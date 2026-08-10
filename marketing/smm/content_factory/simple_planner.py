import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Получаем API ключ из .env
api_key = os.getenv('AI_API_KEY')
base_url = os.getenv('AI_API_BASE_URL')

print(f"Использую API: {base_url}")
print(f"Ключ: {api_key[:20]}...\n")

# Читаем базу знаний
with open('knowledge_base.md', 'r', encoding='utf-8') as f:
    knowledge = f.read()

# Формируем запрос
prompt = f"""Ты — SMM-стратег для клиники эстетической медицины ARclinic (Анна Резник).

Информация о бренде:
{knowledge[:3000]}

Создай контент-план для Instagram на месяц (8-10 постов).

Учти:
- Экспертный, тёплый голос с лёгкой иронией
- Аудитория: женщины 30-55
- Запреты: не давать диагнозы без осмотра

Формат ответа (простой список):
1. [Тема поста] - [тип: экспертный/личный/полезный] - [ключевая мысль]
2. ...
"""

# Запрос к DeepSeek API
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": os.getenv('AI_MODEL', 'deepseek/deepseek-v4-pro'),
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 2000
}

print("🎨 Генерация контент-плана...")
print("⏳ Подождите 20-30 секунд...\n")

try:
    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=data,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        print("\n" + "="*60)
        print("📱 КОНТЕНТ-ПЛАН ДЛЯ INSTAGRAM ARclinic")
        print("="*60)
        print(content)
        
        # Сохраняем в файл
        with open("content_plan_instagram.md", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("\n✅ Контент-план сохранён в content_plan_instagram.md")
    else:
        print(f"❌ Ошибка API: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Ошибка: {e}")