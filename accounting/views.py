from rest_framework import viewsets
from .models import Invoice, Payment, Transaction, SalaryCalculation, CashRegister
from .serializers import (
    InvoiceSerializer, PaymentSerializer, TransactionSerializer,
    SalaryCalculationSerializer, CashRegisterSerializer,
)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filterset_fields = ["status"]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_fields = ["transaction_type", "transaction_date"]


class SalaryCalculationViewSet(viewsets.ModelViewSet):
    queryset = SalaryCalculation.objects.all()
    serializer_class = SalaryCalculationSerializer


class CashRegisterViewSet(viewsets.ModelViewSet):
    queryset = CashRegister.objects.all()
    serializer_class = CashRegisterSerializer
