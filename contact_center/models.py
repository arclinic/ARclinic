from django.db import models
from shared.models import BaseModel, NamedModel


class CallSession(BaseModel):
    STATUS_CHOICES = [("ringing", "Звонит"), ("in_progress", "Разговор"), ("completed", "Завершен"), ("missed", "Пропущен")]
    caller_phone = models.CharField(max_length=20, verbose_name="Номер звонящего")
    operator_id = models.IntegerField(verbose_name="ID оператора", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ringing", verbose_name="Статус")
    started_at = models.DateTimeField(verbose_name="Начало звонка", auto_now_add=True)
    ended_at = models.DateTimeField(verbose_name="Конец звонка", null=True, blank=True)
    duration = models.IntegerField(verbose_name="Длительность (сек)", default=0)
    recording_url = models.URLField(verbose_name="Запись разговора", blank=True)

    class Meta:
        verbose_name = "Звонок"
        verbose_name_plural = "Звонки"


class ChatSession(BaseModel):
    SOURCE_CHOICES = [("site", "Сайт"), ("whatsapp", "WhatsApp"), ("telegram", "Telegram"), ("viber", "Viber")]
    STATUS_CHOICES = [("active", "Активен"), ("waiting", "Ожидание оператора"), ("closed", "Закрыт")]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name="Источник")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting", verbose_name="Статус")
    client_name = models.CharField(max_length=255, verbose_name="Имя клиента", blank=True)
    client_identifier = models.CharField(max_length=255, verbose_name="Идентификатор клиента")
    operator_id = models.IntegerField(verbose_name="ID оператора", null=True, blank=True)
    closed_at = models.DateTimeField(verbose_name="Закрыт", null=True, blank=True)

    class Meta:
        verbose_name = "Чат-сессия"
        verbose_name_plural = "Чат-сессии"


class Message(BaseModel):
    MESSAGE_DIRECTION = [("incoming", "Входящее"), ("outgoing", "Исходящее")]
    chat = models.ForeignKey(ChatSession, on_delete=models.CASCADE, verbose_name="Чат")
    direction = models.CharField(max_length=10, choices=MESSAGE_DIRECTION, verbose_name="Направление")
    text = models.TextField(verbose_name="Текст сообщения")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Отправлено")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["sent_at"]


class Ticket(BaseModel):
    PRIORITY_CHOICES = [("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий"), ("urgent", "Срочный")]
    STATUS_CHOICES = [("new", "Новый"), ("in_progress", "В работе"), ("waiting", "Ожидание"), ("resolved", "Решен"), ("closed", "Закрыт")]
    CATEGORY_CHOICES = [("question", "Вопрос"), ("complaint", "Жалоба"), ("request", "Запрос"), ("other", "Другое")]
    subject = models.CharField(max_length=255, verbose_name="Тема")
    description = models.TextField(verbose_name="Описание")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium", verbose_name="Приоритет")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="question", verbose_name="Категория")
    assigned_to = models.IntegerField(verbose_name="Назначен на", null=True, blank=True)
    client_phone = models.CharField(max_length=20, verbose_name="Телефон клиента", blank=True)
    client_email = models.EmailField(verbose_name="Email клиента", blank=True)
    resolved_at = models.DateTimeField(verbose_name="Решен", null=True, blank=True)
    sla_deadline = models.DateTimeField(verbose_name="SLA до", null=True, blank=True)

    class Meta:
        verbose_name = "Тикет"
        verbose_name_plural = "Тикеты"


class TicketComment(BaseModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name="Тикет")
    author_id = models.IntegerField(verbose_name="ID автора")
    text = models.TextField(verbose_name="Текст")
    is_internal = models.BooleanField(default=False, verbose_name="Внутренний")

    class Meta:
        verbose_name = "Комментарий к тикету"
        verbose_name_plural = "Комментарии к тикетам"


class KnowledgeBaseArticle(NamedModel):
    CATEGORY_CHOICES = [("faq", "FAQ"), ("script", "Скрипт"), ("instruction", "Инструкция")]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория")
    content = models.TextField(verbose_name="Содержание")
    tags = models.JSONField(verbose_name="Теги", default=list, blank=True)

    class Meta:
        verbose_name = "Статья базы знаний"
        verbose_name_plural = "Статьи базы знаний"


class Script(NamedModel):
    CATEGORY_CHOICES = [("greeting", "Приветствие"), ("appointment", "Запись"), ("complaint", "Обработка жалобы"), ("farewell", "Прощание")]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория")
    content = models.TextField(verbose_name="Скрипт")

    class Meta:
        verbose_name = "Скрипт оператора"
        verbose_name_plural = "Скрипты операторов"


class OperatorStat(BaseModel):
    operator_id = models.IntegerField(verbose_name="ID оператора")
    date = models.DateField(verbose_name="Дата")
    calls_taken = models.IntegerField(default=0, verbose_name="Принято звонков")
    chats_handled = models.IntegerField(default=0, verbose_name="Чатов обработано")
    tickets_resolved = models.IntegerField(default=0, verbose_name="Тикетов решено")
    avg_response_time = models.IntegerField(default=0, verbose_name="Ср. время ответа (сек)")
    avg_talk_time = models.IntegerField(default=0, verbose_name="Ср. длительность разговора (сек)")
    csat_score = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="CSAT")

    class Meta:
        verbose_name = "Статистика оператора"
        verbose_name_plural = "Статистики операторов"
        unique_together = ["operator_id", "date"]


class Integration(NamedModel):
    INTEGRATION_TYPES = [("whatsapp", "WhatsApp"), ("telegram", "Telegram"), ("viber", "Viber"), ("sip", "SIP-телефония")]
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPES, verbose_name="Тип")
    api_key = models.CharField(max_length=255, verbose_name="API ключ", blank=True)
    webhook_url = models.URLField(verbose_name="Webhook URL", blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Активно")
    settings = models.JSONField(verbose_name="Настройки", default=dict, blank=True)

    class Meta:
        verbose_name = "Интеграция"
        verbose_name_plural = "Интеграции"
