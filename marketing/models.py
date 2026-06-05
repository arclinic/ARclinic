from django.db import models
from shared.models import NamedModel, BaseModel


class Campaign(NamedModel):
    CAMPAIGN_TYPES = [
        ("context", "Контекстная реклама"),
        ("social", "Социальные сети"),
        ("email", "E-mail рассылка"),
        ("seo", "SEO"),
        ("offline", "Оффлайн"),
    ]
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("active", "Активна"),
        ("paused", "Приостановлена"),
        ("completed", "Завершена"),
    ]
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES, verbose_name="Тип кампании")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Статус")
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Бюджет")
    spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Потрачено")
    start_date = models.DateField(verbose_name="Дата начала", null=True, blank=True)
    end_date = models.DateField(verbose_name="Дата окончания", null=True, blank=True)

    class Meta:
        verbose_name = "Рекламная кампания"
        verbose_name_plural = "Рекламные кампании"

    def roi(self):
        if self.budget and self.spent:
            return float(self.spent / self.budget * 100)
        return 0


class Lead(BaseModel):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("contacted", "Связались"),
        ("appointed", "Записан"),
        ("visited", "Посетил"),
        ("lost", "Потерян"),
    ]
    SOURCE_CHOICES = [
        ("site", "Сайт"),
        ("social", "Соцсети"),
        ("call", "Звонок"),
        ("referral", "Рекомендация"),
    ]
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name="Источник")
    campaign = models.ForeignKey(
        Campaign, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кампания"
    )
    comment = models.TextField(verbose_name="Комментарий", blank=True)

    class Meta:
        verbose_name = "Лид"
        verbose_name_plural = "Лиды"

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        return " ".join(p for p in parts if p)


class EmailTemplate(NamedModel):
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Шаблон письма")

    class Meta:
        verbose_name = "Шаблон письма"
        verbose_name_plural = "Шаблоны писем"


class MailingCampaign(BaseModel):
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("scheduled", "Запланирована"),
        ("sending", "Отправляется"),
        ("sent", "Отправлена"),
    ]
    name = models.CharField(max_length=255, verbose_name="Название рассылки")
    template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT, verbose_name="Шаблон")
    recipient_list = models.TextField(verbose_name="Список получателей", help_text="Email через запятую")
    scheduled_at = models.DateTimeField(verbose_name="Запланирована на", null=True, blank=True)
    sent_at = models.DateTimeField(verbose_name="Отправлена", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Статус")
    opened_count = models.IntegerField(default=0, verbose_name="Открыто")
    clicked_count = models.IntegerField(default=0, verbose_name="Переходов")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class SEOKeyword(NamedModel):
    keyword = models.CharField(max_length=255, verbose_name="Ключевое слово")
    position = models.IntegerField(verbose_name="Позиция в выдаче", null=True, blank=True)
    volume = models.IntegerField(verbose_name="Частотность", default=0)
    page_url = models.URLField(verbose_name="URL страницы", blank=True)

    class Meta:
        verbose_name = "SEO-ключевое слово"
        verbose_name_plural = "SEO-ключевые слова"


class ContentPage(NamedModel):
    slug = models.SlugField(unique=True, verbose_name="URL-идентификатор")
    content = models.TextField(verbose_name="Содержание", blank=True)
    meta_title = models.CharField(max_length=255, verbose_name="Meta Title", blank=True)
    meta_description = models.TextField(verbose_name="Meta Description", blank=True)
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "Контентная страница"
        verbose_name_plural = "Контентные страницы"


class ABTest(NamedModel):
    page_url = models.URLField(verbose_name="URL страницы")
    variant_a = models.TextField(verbose_name="Вариант A")
    variant_b = models.TextField(verbose_name="Вариант B")
    starts_at = models.DateTimeField(verbose_name="Начало", null=True, blank=True)
    ends_at = models.DateTimeField(verbose_name="Окончание", null=True, blank=True)
    a_views = models.IntegerField(default=0, verbose_name="Просмотров A")
    b_views = models.IntegerField(default=0, verbose_name="Просмотров B")
    a_conversions = models.IntegerField(default=0, verbose_name="Конверсий A")
    b_conversions = models.IntegerField(default=0, verbose_name="Конверсий B")

    class Meta:
        verbose_name = "A/B тест"
        verbose_name_plural = "A/B тесты"


class AnalyticsEvent(BaseModel):
    EVENT_TYPES = [
        ("page_view", "Просмотр страницы"),
        ("form_submit", "Отправка формы"),
        ("click", "Клик"),
        ("call", "Звонок"),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name="Тип события")
    page_url = models.URLField(verbose_name="URL страницы", blank=True)
    referrer = models.URLField(verbose_name="Откуда пришел", blank=True)
    session_id = models.CharField(max_length=100, verbose_name="ID сессии", blank=True)
    data = models.JSONField(verbose_name="Данные события", default=dict, blank=True)

    class Meta:
        verbose_name = "Событие аналитики"
        verbose_name_plural = "События аналитики"
