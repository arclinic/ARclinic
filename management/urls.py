from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, EmployeeViewSet, DoctorProfileViewSet,
    AppointmentViewSet, ServiceViewSet, MedicalRecordViewSet,
)

router = DefaultRouter()
router.register(r"patients", PatientViewSet)
router.register(r"employees", EmployeeViewSet)
router.register(r"doctors", DoctorProfileViewSet)
router.register(r"appointments", AppointmentViewSet)
router.register(r"services", ServiceViewSet)
router.register(r"medical-records", MedicalRecordViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
