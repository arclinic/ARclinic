from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InvoiceViewSet, PaymentViewSet, TransactionViewSet,
    SalaryCalculationViewSet, CashRegisterViewSet,
)

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"transactions", TransactionViewSet)
router.register(r"salaries", SalaryCalculationViewSet)
router.register(r"cash-registers", CashRegisterViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
