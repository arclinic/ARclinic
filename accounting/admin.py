from django.contrib import admin
from .models import Account, Invoice, Payment, Transaction, CashRegister, Budget, TaxReport


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "account_type"]
    list_filter = ["account_type"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["number", "client_name", "amount", "status", "issued_at", "due_at"]
    list_filter = ["status"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["amount", "payment_method", "paid_at"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["transaction_type", "amount", "transaction_date", "debit_account", "credit_account"]
    list_filter = ["transaction_type"]


@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ["name", "balance"]
