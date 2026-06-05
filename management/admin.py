from django.contrib import admin
from .models import Patient, Employee, DoctorProfile, Service, Appointment, MedicalRecord


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "phone", "created_at"]
    search_fields = ["last_name", "first_name", "phone"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "position", "phone"]
    list_filter = ["position"]


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ["employee", "specialization"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["patient", "doctor", "start_at", "status", "is_paid"]
    list_filter = ["status"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "duration"]


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["patient", "doctor", "appointment"]
