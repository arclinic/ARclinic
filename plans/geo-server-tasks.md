# Задачи GEO: что делать на сервере

## Статус выполнения (01.06.2026)

### ✅ Сделано
1. **robots.txt** — AI-краулеры разблокированы, Sitemap исправлен, UTM удалён
2. **llms.txt** — создан и доступен на /llms.txt

### ❌ Требует доступа к серверу Bitrix

#### 1. Article/BlogPosting schema
Добавить в шаблон блога (`/local/templates/arclinic/components/bitrix/news.detail/blog/` или аналогичный):

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "<?= $arResult['NAME'] ?>",
  "description": "<?= $arResult['PREVIEW_TEXT'] ?>",
  "url": "<?= $arResult['DETAIL_PAGE_URL'] ?>",
  "datePublished": "<?= $arResult['DATE_ACTIVE_FROM'] ?>",
  "dateModified": "<?= $arResult['TIMESTAMP_X'] ?>",
  "author": {
    "@type": "Person",
    "name": "Анна Вячеславовна Резник",
    "jobTitle": "Кандидат медицинских наук, врач-косметолог"
  },
  "publisher": {
    "@type": "Organization",
    "name": "ARclinic",
    "logo": {
      "@type": "ImageObject",
      "url": "https://arclinic.ru/local/templates/arclinic/img/favicon/apple-touch-icon.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "<?= $arResult['DETAIL_PAGE_URL'] ?>"
  },
  "medicalAudience": {
    "@type": "PeopleAudience",
    "suggestedMinAge": 18
  }
}
</script>
```

#### 2. Author + date в мета-тегах
В `<head>` шаблона добавить:
```html
<meta property="article:published_time" content="<?= $arResult['DATE_ACTIVE_FROM'] ?>">
<meta property="article:modified_time" content="<?= $arResult['TIMESTAMP_X'] ?>">
<meta property="article:author" content="Анна Вячеславовна Резник">
```

#### 3. Person schema для врачей
На страницах врачей (`/doctors/`) добавить:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Physician",
  "name": "Анна Вячеславовна Резник",
  "jobTitle": "Врач-косметолог, к.м.н.",
  "medicalSpecialty": "Dermatology",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Санкт-Петербург",
    "streetAddress": "Московский пр., 187"
  },
  "telephone": "+78129436900",
  "url": "https://arclinic.ru/doctors/reznik-anna-vyacheslavovna/"
}
</script>
```

## Приоритет
1. Article schema в блоге (влияет на видимость в AI)
2. Person schema для врачей
3. Meta-теги автора/даты

## Как применить
1. Войти в Bitrix admin → Структура сайта →_local/templates/arclinic/
2. Найти шаблон detail страницы блога
3. Добавить JSON-LD код перед закрытием `</head>` или в начало `<body>`
4. Сохранить и очистить кеш Bitrix
