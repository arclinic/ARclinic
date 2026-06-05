from django.db import models
from shared.models import BaseModel, NamedModel


class Account(NamedModel):
    ACCOUNT_TYPES = [("active", "Активный"), ("passive", "Пассивный"), ("active_passive", "Активно-пассивный")]
    code = models.CharField(max_length=8, verbose_name="Код счета", unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name="Тип счета")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родительский счет")

    class Meta:
        verbose_name = "Счет учета"
        verbose_name_plural = "Счета учета"


class Transaction(BaseModel):
    TRANSACTION_TYPES = [("income", "Доход"), ("expense", "Расход"), ("transfer", "Перевод")]
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name="Тип")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    description = models.TextField(verbose_name="Описание", blank=True)
    transaction_date = models.DateField(verbose_name="Дата операции")
    debit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="debit_transactions", verbose_name="Дебет")
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="credit_transactions", verbose_name="Кредит")

    class Meta:
        verbose_name = "Проводка"
        verbose_name_plural = "Проводки"


class Invoice(BaseModel):
    STATUS_CHOICES = [("draft", "Черновик"), ("sent", "Отправлен"), ("paid", "Оплачен"), ("overdue", "Просрочен"), ("cancelled", "Отменен")]
    number = models.CharField(max_length=50, verbose_name="Номер счета", unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Статус")
    client_name = models.CharField(max_length=255, verbose_name="Клиент")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    issued_at = models.DateField(verbose_name="Дата выставления")
    due_at = models.DateField(verbose_name="Оплатить до")
    paid_at = models.DateField(verbose_name="Оплачен", null=True, blank=True)

    class Meta:
        verbose_name = "Счет на оплату"
        verbose_name_plural = "Счета на оплату"


class Payment(BaseModel):
    PAYMENT_METHODS = [("cash", "Наличные"), ("card", "Карта"), ("transfer", "Безналичный перевод"), ("online", "Онлайн-оплата")]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Счет", null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Способ оплаты")
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"


class SalaryCalculation(BaseModel):
    STATUS_CHOICES = [("draft", "Черновик"), ("approved", "Утвержден"), ("paid", "Выплачен")]
    employee_id = models.IntegerField(verbose_name="ID сотрудника")
    period_start = models.DateField(verbose_name="Начало периода")
    period_end = models.DateField(verbose_name="Конец периода")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Оклад")
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Премия")
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Удержания")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="К выдаче")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Статус")
    paid_at = models.DateField(verbose_name="Дата выплаты", null=True, blank=True)

    class Meta:
        verbose_name = "Расчет зарплаты"
        verbose_name_plural = "Расчеты зарплаты"


class CashRegister(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Название кассы")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Остаток")

    class Meta:
        verbose_name = "Касса"
        verbose_name_plural = "Кассы"


class CashOperation(BaseModel):
    OPERATION_TYPES = [("incoming", "Приход"), ("outgoing", "Расход")]
    cash_register = models.ForeignKey(CashRegister, on_delete=models.CASCADE, verbose_name="Касса")
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES, verbose_name="Тип операции")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    description = models.TextField(verbose_name="Описание", blank=True)
    operated_at = models.DateTimeField(verbose_name="Дата операции")

    class Meta:
        verbose_name = "Кассовая операция"
        verbose_name_plural = "Кассовые операции"


class BankStatement(BaseModel):
    account_number = models.CharField(max_length=20, verbose_name="Номер счета")
    transaction_id = models.CharField(max_length=100, verbose_name="ID транзакции", unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    description = models.TextField(verbose_name="Назначение платежа", blank=True)
    counterparty = models.CharField(max_length=255, verbose_name="Контрагент", blank=True)
    transaction_date = models.DateTimeField(verbose_name="Дата операции")

    class Meta:
        verbose_name = "Банковская выписка"
        verbose_name_plural = "Банковские выписки"


class CostCenter(NamedModel):
    code = models.CharField(max_length=10, verbose_name="Код ЦФО")
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Бюджет")

    class Meta:
        verbose_name = "Центр затрат"
        verbose_name_plural = "Центры затрат"


class Budget(NamedModel):
    PERIOD_CHOICES = [("month", "Месяц"), ("quarter", "Квартал"), ("year", "Год")]
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, verbose_name="Период")
    period_start = models.DateField(verbose_name="Начало периода")
    period_end = models.DateField(verbose_name="Конец периода")
    planned = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="План")
    actual = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Факт")
    cost_center = models.ForeignKey(CostCenter, on_delete=models.CASCADE, verbose_name="ЦФО", null=True, blank=True)

    class Meta:
        verbose_name = "Бюджет"
        verbose_name_plural = "Бюджеты"


class TaxReport(BaseModel):
    REPORT_TYPES = [("vat", "НДС"), ("profit", "Налог на прибыль"), ("property", "Налог на имущество"), ("simplified", "УСН")]
    STATUS_CHOICES = [("draft", "Черновик"), ("submitted", "Сдан"), ("paid", "Оплачен")]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="Тип отчета")
    period = models.CharField(max_length=7, verbose_name="Период", help_text="ММ.ГГГГ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Статус")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма налога")
    filed_at = models.DateField(verbose_name="Дата сдачи", null=True, blank=True)

    class Meta:
        verbose_name = "Налоговый отчет"
        verbose_name_plural = "Налоговые отчеты"
