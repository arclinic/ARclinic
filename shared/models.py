import uuid
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class NamedModel(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Название")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class PersonModel(BaseModel):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, verbose_name="Отчество")
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)

    class Meta:
        abstract = True

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)

    def __str__(self):
        return self.full_name
