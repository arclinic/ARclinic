import instaloader
import json
import os
from datetime import datetime

# Создаём папку для результатов
today = datetime.now().strftime('%Y-%m-%d')
output_dir = f"output/research/instagram/{today}"
os.makedirs(output_dir, exist_ok=True)

# Инициализация
L = instaloader.Instaloader()

# Аккаунт для парсинга
username = "arclinic"

print(f"🔍 Парсинг Instagram аккаунта: {username}")
print("⏳ Подождите, собираем посты...\n")

try:
    # Загружаем профиль
    profile = instaloader.Profile.from_username(L.context, username)
    
    posts_data = []
    count = 0
    
    # Собираем посты (максимум 30)
    for post in profile.get_posts():
        if count >= 30:
            break
            
        post_info = {
            "id": post.shortcode,
            "url": f"https://www.instagram.com/p/{post.shortcode}/",
            "caption": post.caption if post.caption else "",
            "likes": post.likes,
            "comments": post.comments,
            "timestamp": post.date_utc.isoformat(),
            "is_video": post.is_video,
            "video_url": post.video_url if post.is_video else None
        }
        posts_data.append(post_info)
        count += 1
        print(f"  ✅ Собран пост {count}: {post_info['url'][:40]}...")
    
    # Сохраняем в JSON
    with open(f"{output_dir}/raw.json", "w", encoding="utf-8") as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Готово! Собрано {len(posts_data)} постов")
    print(f"📁 Результат сохранён в: {output_dir}/raw.json")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("\n💡 Если аккаунт закрытый, нужен логин/пароль")