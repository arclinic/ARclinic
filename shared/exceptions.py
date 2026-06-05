from rest_framework.exceptions import APIException


class AppointmentConflict(APIException):
    status_code = 409
    default_detail = "Время приема пересекается с существующей записью"


class InsufficientStock(APIException):
    status_code = 400
    default_detail = "Недостаточно товара на складе"


class PatientNotFound(APIException):
    status_code = 404
    default_detail = "Пациент не найден"
