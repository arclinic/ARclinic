from django.db import models
from shared.models import BaseModel, NamedModel, PersonModel


class Patient(PersonModel):
    SEX_CHOICES = [("M", "Мужской"), ("F", "Женский")]
    date_of_birth = models.DateField(verbose_name="Дата рождения", null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name="Пол", blank=True)
    snils = models.CharField(max_length=14, verbose_name="СНИЛС", blank=True)
    policy_number = models.CharField(max_length=30, verbose_name="Номер полиса", blank=True)
    address = models.TextField(verbose_name="Адрес", blank=True)
    notes = models.TextField(verbose_name="Заметки", blank=True)
    tags = models.JSONField(verbose_name="Теги", default=list, blank=True)

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["phone"]),
        ]


class Employee(PersonModel):
    POSITION_CHOICES = [
        ("doctor", "Врач"),
        ("nurse", "Медсестра"),
        ("admin", "Администратор"),
        ("accountant", "Бухгалтер"),
        ("manager", "Управляющий"),
        ("operator", "Оператор"),
    ]
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name="Должность")
    hired_at = models.DateField(verbose_name="Дата приема", auto_now_add=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Оклад")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class DoctorProfile(BaseModel):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    specialization = models.CharField(max_length=255, verbose_name="Специализация")
    license_number = models.CharField(max_length=50, verbose_name="Номер лицензии", blank=True)
    appointment_duration = models.IntegerField(default=30, verbose_name="Длительность приема (мин)")

    class Meta:
        verbose_name = "Профиль врача"
        verbose_name_plural = "Профили врачей"


class Service(NamedModel):
    duration = models.IntegerField(verbose_name="Длительность (мин)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    is_online = models.BooleanField(default=False, verbose_name="Доступна онлайн-запись")
    description = models.TextField(verbose_name="Описание", blank=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


class Department(NamedModel):
    floor = models.IntegerField(verbose_name="Этаж", null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)

    class Meta:
        verbose_name = "Отделение"
        verbose_name_plural = "Отделения"


class Schedule(BaseModel):
    DAY_CHOICES = [
        (0, "Понедельник"), (1, "Вторник"), (2, "Среда"),
        (3, "Четверг"), (4, "Пятница"), (5, "Суббота"), (6, "Воскресенье"),
    ]
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Врач")
    day_of_week = models.IntegerField(choices=DAY_CHOICES, verbose_name="День недели")
    start_time = models.TimeField(verbose_name="Начало работы")
    end_time = models.TimeField(verbose_name="Конец работы")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"
        unique_together = ["doctor", "day_of_week"]


class Appointment(BaseModel):
    STATUS_CHOICES = [
        ("scheduled", "Запланирован"), ("confirmed", "Подтвержден"),
        ("in_progress", "В процессе"), ("completed", "Завершен"),
        ("cancelled", "Отменен"), ("no_show", "Не пришел"),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Пациент")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Врач")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name="Услуга")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled", verbose_name="Статус")
    start_at = models.DateTimeField(verbose_name="Начало приема")
    end_at = models.DateTimeField(verbose_name="Окончание приема")
    notes = models.TextField(verbose_name="Заметки", blank=True)
    is_paid = models.BooleanField(default=False, verbose_name="Оплачен")

    class Meta:
        verbose_name = "Запись на прием"
        verbose_name_plural = "Записи на прием"
        indexes = [
            models.Index(fields=["start_at", "doctor"]),
            models.Index(fields=["patient", "status"]),
        ]


class MedicalRecord(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Пациент")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, verbose_name="Врач")
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, verbose_name="Прием", null=True, blank=True
    )
    complaint = models.TextField(verbose_name="Жалобы", blank=True)
    diagnosis = models.TextField(verbose_name="Диагноз", blank=True)
    prescription = models.TextField(verbose_name="Назначения", blank=True)
    notes = models.TextField(verbose_name="Дополнительно", blank=True)

    class Meta:
        verbose_name = "Медицинская карта"
        verbose_name_plural = "Медицинские карты"


class Document(NamedModel):
    DOCUMENT_TYPES = [
        ("contract", "Договор"), ("consent", "Согласие"),
        ("referral", "Направление"), ("certificate", "Справка"),
    ]
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name="Тип документа")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Пациент")
    file = models.FileField(verbose_name="Файл", upload_to="documents/%Y/%m/")
    signed_at = models.DateTimeField(verbose_name="Подписан", null=True, blank=True)

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"


class Supplier(NamedModel):
    contact_person = models.CharField(max_length=255, verbose_name="Контактное лицо", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)
    inn = models.CharField(max_length=12, verbose_name="ИНН", blank=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"


class InventoryItem(NamedModel):
    UNIT_CHOICES = [("pcs", "шт"), ("pack", "уп"), ("kg", "кг"), ("l", "л")]
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="pcs", verbose_name="Единица измерения")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Количество")
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Мин. запас")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Цена за ед.")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Поставщик")

    class Meta:
        verbose_name = "Товар/материал"
        verbose_name_plural = "Товары/материалы"


class InventoryTransaction(BaseModel):
    TRANSACTION_TYPES = [("incoming", "Поступление"), ("outgoing", "Списание"), ("write_off", "Уценка")]
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, verbose_name="Товар")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Тип операции")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    comment = models.TextField(verbose_name="Комментарий", blank=True)

    class Meta:
        verbose_name = "Движение товара"
        verbose_name_plural = "Движения товаров"
