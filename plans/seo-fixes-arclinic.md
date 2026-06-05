# Продолжение SEO-правок arclinic.ru

## Что уже сделано
- Проведён аудит (seo-audit-arclinic.md)
- Установлен Claude SEO (25 sub-skills)
- Ты залогинилась в админке Bitrix

## Что делать
Начинай с пункта 1 и двигайся по порядку.

---

### 1. Перегенерация sitemap.xml (критично)
Bitrix: **Настройки > Поисковая оптимизация > Карты сайта**
- Нажать «Удалить все» (старые кривые)
- Создать новую: тип «Авто-генерация», домен `https://arclinic.ru`
- Сохранить и проверить: открыть `https://arclinic.ru/sitemap.xml` — должны быть URL с `arclinic.ru`, не `localhost`

### 2. Title и Meta description на главной
Bitrix: **Контент > Структура сайта > Главная страница** (или Страницы и разделы)
- Найти страницу `/` (главная)
- Вкладка «SEO»
- Title: `ARclinic — Центр антивозрастной медицины и косметологии в СПб`
- Meta description: `Клиника антивозрастной медицины и косметологии ARclinic в Санкт-Петербурге. Косметология, гинекология, эндокринология, диетология. Запись по телефону +7 (812) 943-69-00`
- Сохранить

### 3. Open Graph (og:url)
Bitrix: **Контент > Структура сайта > Шаблоны сайта**
- Найти шаблон `arclinic`
- В файле `header.php` (или где прописаны og-теги)
- Найти строку `og:url` и заменить `http://` на `https://`

### 4. JSON-LD Schema разметка
Добавить в `header.php` шаблона перед `</head>`. Код:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MedicalBusiness",
  "name": "ARclinic",
  "description": "Центр антивозрастной медицины и косметологии",
  "url": "https://arclinic.ru",
  "telephone": "+78122408382",
  "email": "info@arclinic.ru",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "ул. Верейская, д. 44, к. 2",
    "addressLocality": "Санкт-Петербург",
    "addressCountry": "RU"
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
      "opens": "10:00",
      "closes": "20:00"
    }
  ],
  "medicalSpecialty": ["CosmeticDermatology", "Gynecology", "Endocrinology", "Neurology", "Dietetics"],
  "founder": {
    "@type": "Person",
    "name": "Анна Вячеславовна Резник",
    "credential": "Кандидат медицинских наук"
  }
}
</script>
```

### 5. Canonical URL
Bitrix: **Настройки > Настройки продукта > SEO**
- Включить автогенерацию canonical URL для всех страниц
- Если нет такой опции — добавить в `header.php`:
  ```php
  <?php if (!defined("B_PROLOG_INCLUDED") || B_PROLOG_INCLUDED!==true) die(); ?>
  <link rel="canonical" href="https://arclinic.ru<?=$APPLICATION->GetCurPageParam()?>" />
  ```

---

## Как проверить результат
- Sitemap: открыть `https://arclinic.ru/sitemap.xml` — все URL должны быть с `arclinic.ru`
- Schema: использовать валидатор https://validator.schema.org/ — ввести `https://arclinic.ru`
- Title: открыть `https://arclinic.ru` — вкладка браузера должна показывать полный заголовок

## Вопросы?
Если на каком-то шаге непонятно — напиши, я подскажу.
