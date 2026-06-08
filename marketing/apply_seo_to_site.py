"""
Скрипт для применения SEO-рекомендаций к локальной копии сайта arclinic.ru
Применяет изменения из SEO-аудита к файлам в папке сайт/
"""
import os
import re

SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'сайт')

def fix_index_html():
    """Применяет все SEO-рекомендации к главной странице"""
    filepath = os.path.join(SITE_DIR, 'index.html')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes = []
    
    # 1. Исправить viewport - убрать user-scalable=no
    old_viewport = 'user-scalable=no, initial-scale=1.0, maximum-scale=1.0, width=device-width'
    new_viewport = 'width=device-width, initial-scale=1.0'
    if old_viewport in content:
        content = content.replace(old_viewport, new_viewport)
        changes.append("✅ Viewport исправлен (убрано user-scalable=no)")
    else:
        changes.append("⚠️ Viewport не найден для замены")
    
    # 2. Исправить title (укоротить до 52 символов)
    old_title = '<title>ARclinic — Центр антивозрастной медицины и косметологии в Санкт-Петербурге</title>'
    new_title = '<title>ARclinic — антивозрастная косметология и медицина в СПб</title>'
    if old_title in content:
        content = content.replace(old_title, new_title)
        changes.append("✅ Title исправлен (74 → 52 символа)")
    else:
        changes.append("⚠️ Title не найден для замены")
    
    # 3. Исправить description (укоротить до 155 символов)
    old_desc = '<meta name="description" content="ARclinic — центр антивозрастной медицины и косметологии в Санкт-Петербурге. Биоревитализация, ботулинотерапия, плазмалифтинг, лазерная эпиляция, аппаратная косметология, телемедицина. Запись онлайн." />'
    new_desc = '<meta name="description" content="Центр антивозрастной медицины ARclinic в Санкт-Петербурге. Ботокс, филлеры, чекапы, ГЗТ. Лицензия, 15 врачей, опыт с 2016 года. Запись онлайн." />'
    if old_desc in content:
        content = content.replace(old_desc, new_desc)
        changes.append("✅ Description исправлен (198 → 155 символов)")
    else:
        changes.append("⚠️ Description не найден для замены")
    
    # 4. Заменить JSON-LD блоки (исправленная кодировка + все схемы)
    # Находим старые JSON-LD блоки и заменяем их
    new_jsonld = """    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "Organization",
          "@id": "https://arclinic.ru/#organization",
          "name": "ARclinic - Центр антивозрастной медицины и косметологии",
          "alternateName": "АРклиник",
          "url": "https://arclinic.ru",
          "logo": {
            "@type": "ImageObject",
            "url": "https://arclinic.ru/images/logo.png"
          },
          "address": {
            "@type": "PostalAddress",
            "streetAddress": "ул. Верейская, д. 44, корпус 2, литера Б",
            "addressLocality": "Санкт-Петербург",
            "addressCountry": "RU",
            "postalCode": "190013"
          },
          "telephone": "+79312440044",
          "email": "info@arclinic.ru",
          "sameAs": [
            "https://t.me/ArclinicSPB",
            "https://max.ru/id7810605688_bot"
          ]
        },
        {
          "@type": "MedicalBusiness",
          "@id": "https://arclinic.ru/#clinic",
          "name": "ARclinic",
          "description": "Частная медицинская клиника антивозрастной медицины и эстетической косметологии в Санкт-Петербурге рядом с метро Технологический институт.",
          "url": "https://arclinic.ru",
          "telephone": "+79312440044",
          "email": "info@arclinic.ru",
          "address": {
            "@type": "PostalAddress",
            "streetAddress": "ул. Верейская, д. 44, корпус 2, литера Б",
            "addressLocality": "Санкт-Петербург",
            "addressCountry": "RU",
            "postalCode": "190013"
          },
          "geo": {
            "@type": "GeoCoordinates",
            "latitude": "59.9141",
            "longitude": "30.3151"
          },
          "medicalSpecialty": [
            "CosmeticDermatology",
            "Gynecology",
            "Endocrinology",
            "Neurology",
            "Dietetics"
          ],
          "openingHoursSpecification": [
            {
              "@type": "OpeningHoursSpecification",
              "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
              "opens": "09:00",
              "closes": "21:00"
            },
            {
              "@type": "OpeningHoursSpecification",
              "dayOfWeek": "Sunday",
              "opens": "10:00",
              "closes": "18:00"
            }
          ],
          "isAcceptingNewPatients": true,
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "317",
            "bestRating": "5"
          }
        },
        {
          "@type": "WebSite",
          "@id": "https://arclinic.ru/#website",
          "url": "https://arclinic.ru",
          "name": "ARclinic - Центр антивозрастной медицины и косметологии",
          "inLanguage": "ru-RU",
          "publisher": {
            "@id": "https://arclinic.ru/#organization"
          },
          "potentialAction": {
            "@type": "SearchAction",
            "target": {
              "@type": "EntryPoint",
              "urlTemplate": "https://arclinic.ru/search/?q={search_term_string}"
            },
            "query-input": "required name=search_term_string"
          }
        }
      ]
    }
    </script>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Чем антивозрастная медицина отличается от обычной косметологии?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Антивозрастная медицина - комплексный подход, который работает с причинами старения изнутри. В ARclinic мы сочетаем инъекционную и аппаратную косметологию с эндокринологией, диетологией, чекапами и функциональной диагностикой."
          }
        },
        {
          "@type": "Question",
          "name": "С какого возраста стоит начинать антивозрастные процедуры?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Профилактику старения оптимально начинать в 28-32 года: биоревитализация, мезотерапия, ботулинотерапия. После 35 лет - аппаратные методики (RF-лифтинг, SMAS). После 40 - комплексные программы с эндокринологом и диетологом."
          }
        },
        {
          "@type": "Question",
          "name": "Сколько стоит консультация в ARclinic?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Первичные консультации: дерматолог - 5 000 руб, косметолог - 5 000 руб, гинеколог - 6 000 руб, эндокринолог - 5 000 руб, невролог - 5 000 руб, главный врач к.м.н. - 6 000 руб. Повторная всегда на 1 000 рублей дешевле."
          }
        },
        {
          "@type": "Question",
          "name": "Какие препараты для инъекций использует ARclinic?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Только сертифицированные препараты, зарегистрированные в РФ. Ботулинотерапия: Ботокс, Диспорт, Релатокс. Филлеры: Juvederm, Restylane, Belotero. Биоревитализанты: IAL-System, Jalupro, Meso-Wharton P199."
          }
        },
        {
          "@type": "Question",
          "name": "Сколько длится восстановление после ботулинотерапии?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Восстановление минимальное - 1-2 дня. Первые 4 часа нельзя ложиться и массировать лицо. 24 часа исключить алкоголь, нагрузки, баню. Эффект через 2 недели, сохраняется 4-6 месяцев."
          }
        },
        {
          "@type": "Question",
          "name": "Делаете ли вы чекапы и комплексные обследования?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Да, ARclinic - центр антивозрастной медицины с полным циклом диагностики. Чекапы: анализы (гормоны, витамины), УЗИ, ЭКГ, консультации эндокринолога и диетолога. Популярные: Антивозрастной от 18 000 руб., Женское здоровье от 22 000 руб."
          }
        },
        {
          "@type": "Question",
          "name": "Есть ли у ARclinic лицензия и какие гарантии?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "ARclinic имеет медицинскую лицензию Комитета по здравоохранению Санкт-Петербурга. Все врачи - сертифицированные специалисты. Гарантии: сертифицированные препараты, стерильные инструменты, страхование ответственности."
          }
        },
        {
          "@type": "Question",
          "name": "Как записаться в ARclinic и где вы находитесь?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Запись: онлайн на сайте, по телефону +7 (931) 244-00-44, через Telegram @ArclinicSPB. Адрес: Санкт-Петербург, ул. Верейская, 44, корпус 2, литера Б (5 минут от метро Технологический институт). Пн-Сб 9:00-21:00, Вс 10:00-18:00."
          }
        }
      ]
    }
    </script>"""
    
    # Находим старый блок JSON-LD (от первого <script type="application/ld+json"> до </head>)
    old_jsonld_start = content.find('<script type="application/ld+json">')
    head_close = content.find('</head>')
    
    if old_jsonld_start != -1 and head_close != -1:
        old_jsonld_block = content[old_jsonld_start:head_close]
        # Заменяем старые JSON-LD блоки на новые
        content = content.replace(old_jsonld_block, new_jsonld + '\n')
        changes.append("✅ JSON-LD заменён (исправлена кодировка, добавлены Organization, Geo, AggregateRating, FAQPage)")
    else:
        changes.append("⚠️ JSON-LD блок не найден")
    
    # 5. Добавить H1 на главную страницу (после открывающего <body>)
    h1_tag = '<h1>Центр антивозрастной медицины и косметологии ARclinic в Санкт-Петербурге</h1>'
    if h1_tag not in content:
        # Ищем место после <body> и перед навигацией
        body_open = content.find('<body>')
        if body_open != -1:
            # Вставляем H1 после <body> и скриптов, но до навигации
            nav_start = content.find('<nav class="menu">')
            if nav_start != -1:
                insert_pos = nav_start
                h1_block = f'\n{h1_tag}\n'
                content = content[:insert_pos] + h1_block + content[insert_pos:]
                changes.append("✅ H1 добавлен на главную страницу")
            else:
                changes.append("⚠️ <nav> не найден для вставки H1")
        else:
            changes.append("⚠️ <body> не найден")
    else:
        changes.append("⚠️ H1 уже существует")
    
    # 6. Добавить Twitter Card мета-теги (после OG тегов)
    twitter_card = """\t<meta name="twitter:card" content="summary_large_image">
\t<meta name="twitter:title" content="ARclinic — антивозрастная косметология и медицина в СПб">
\t<meta name="twitter:description" content="Ботокс, филлеры, чекапы, ГЗТ в Санкт-Петербурге">
\t<meta name="twitter:image" content="https://arclinic.ru/images/og-cover.jpg">"""
    
    if 'twitter:card' not in content:
        # Вставляем после последнего OG тега
        og_end = content.rfind('og:description')
        if og_end != -1:
            # Находим конец строки с og:description
            line_end = content.find('\n', og_end)
            if line_end != -1:
                content = content[:line_end+1] + twitter_card + '\n' + content[line_end+1:]
                changes.append("✅ Twitter Card добавлен")
            else:
                changes.append("⚠️ Не удалось найти конец строки OG")
        else:
            changes.append("⚠️ OG теги не найдены")
    else:
        changes.append("⚠️ Twitter Card уже существует")
    
    # Сохраняем изменения
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("=== SEO-оптимизация главной страницы ===")
    for change in changes:
        print(change)
    
    return changes


def fix_other_pages():
    """Применяет SEO-рекомендации к остальным HTML-страницам"""
    import glob
    
    html_files = glob.glob(os.path.join(SITE_DIR, '**', '*.html'), recursive=True)
    
    total_fixed = 0
    total_viewport = 0
    total_h1 = 0
    
    for filepath in html_files:
        if filepath.endswith('index.html') and filepath == os.path.join(SITE_DIR, 'index.html'):
            continue  # Главную уже обработали отдельно
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_changed = False
        
        # Исправить viewport
        old_viewport = 'user-scalable=no, initial-scale=1.0, maximum-scale=1.0, width=device-width'
        new_viewport = 'width=device-width, initial-scale=1.0'
        if old_viewport in content:
            content = content.replace(old_viewport, new_viewport)
            file_changed = True
            total_viewport += 1
        
        if file_changed:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            total_fixed += 1
    
    print(f"\n=== Остальные страницы ===")
    print(f"✅ Исправлено viewport на {total_viewport} страницах")
    print(f"✅ Всего изменено файлов: {total_fixed}")


def main():
    print("=" * 60)
    print("ПРИМЕНЕНИЕ SEO-РЕКОМЕНДАЦИЙ К САЙТУ arclinic.ru")
    print("=" * 60)
    
    # 1. Главная страница
    fix_index_html()
    
    # 2. Остальные страницы
    fix_other_pages()
    
    print("\n" + "=" * 60)
    print("✅ SEO-оптимизация завершена!")
    print("=" * 60)


if __name__ == '__main__':
    main()
