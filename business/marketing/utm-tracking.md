# UTM-метки: структура и внедрение

## Стандартный шаблон UTM
```
?utm_source={source}&utm_medium={medium}&utm_campaign=q3-2026&utm_content={content}&utm_term={term}
```

## Параметры

| Параметр | Назначение | Примеры |
|----------|-----------|---------|
| `utm_source` | Канал трафика | telegram, vk, instagram, yandex, google, email, site |
| `utm_medium` | Тип трафика | social, cpc, organic, email, referral, banner |
| `utm_campaign` | Кампания | q3-2026, men-landing, tg-promo, yandex-test |
| `utm_content` | Конкретный элемент/объявление | post-1, story-2, banner-a, link-header |
| `utm_term` | Ключевое слово | ботулинотерапия-спб, згт-спб |

## Источники

### Сайт (arclinic.ru)
- Ссылки в шапке, подвале, контенте — `?utm_source=site&utm_medium=organic&utm_campaign=q3-2026`
- Кнопка «Записаться» — `?utm_source=site&utm_medium=organic&utm_campaign=q3-2026&utm_content=zapis-btn`

### Telegram (@arclinic1)
- Ссылка на сайт в посте — `?utm_source=tg&utm_medium=social&utm_campaign=q3-2026&utm_content={post-id}`
- Ссылка из описания канала — `?utm_source=tg&utm_medium=social&utm_campaign=q3-2026&utm_content=description`
- Ссылка в сторис/комментарии — `?utm_source=tg&utm_medium=social&utm_campaign=q3-2026&utm_content=story`

### Telegram (забота) (@ArclinicSPB)
- Рассылки — `?utm_source=tg&utm_medium=email_trigger&utm_campaign=retention&utm_content={scenario-id}`

### Telegram Анны Резник (@av_reznik)
- Посты про клинику — `?utm_source=tg&utm_medium=social&utm_campaign=q3-2026&utm_content=av-reznik`

### ВКонтакте
- Пост — `?utm_source=vk&utm_medium=social&utm_campaign=q3-2026&utm_content={post-id}`

### Instagram врачей
- Пост/сторис — `?utm_source=insta&utm_medium=social&utm_campaign=q3-2026&utm_content={doctor-name}`

### Яндекс.Директ
- Объявление — `?utm_source=yandex&utm_medium=cpc&utm_campaign={campaign-name}&utm_term={keyword}`

### ПроДокторов / Google Maps
- Ссылка в профиле — `?utm_source=prodoctorov&utm_medium=referral&utm_campaign=q3-2026`

### Email-рассылки
- Письмо — `?utm_source=email&utm_medium=email&utm_campaign={scenario-name}&utm_content={date}`

## Call Tracking

**Рекомендация:** подключить Яндекс.Коллтрекинг (входит в Яндекс.Директ) или Mango-Office.
- Определяет источник звонка
- Связывает звонок с UTM-меткой (если визит был до звонка)
- Передаёт источник сделки в Bitrix24 CRM

## Настройка в Bitrix24 CRM

Чтобы UTM-метки попадали в сделки:
1. В настройках CRM → Формы → добавить скрытые поля: utm_source, utm_medium, utm_campaign
2. В Источниках сделок: создать одноимённые источники (telegram, vk, instagram, yandex, email, site)
3. Настроить авто-заполнение поля «Источник» из UTM

**Связи:** [[channels]] (каналы) · [[../economics/unit-economics]] (CAC) · [[funnel]] (конверсия) · [[../../plans/2026-05-25-prodvizhenie-arclinic-q3]] (план Q3)
