from django.contrib.auth.models import AbstractUser
from django.db import models


class Resident(AbstractUser):
    class RoleChoices(models.TextChoices):
        VECINO = "VECINO", "Vecino"
        DIRECTIVA = "DIRECTIVA", "Directiva"
        ADMIN = "ADMIN", "Administrador"

    class StatusChoices(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente de Validación"
        ACTIVO = "ACTIVO", "Activo"
        RECHAZADO = "RECHAZADO", "Rechazado"

    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    address = models.CharField(max_length=255, verbose_name="Dirección / Pasaje")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    role = models.CharField(
        max_length=15,
        choices=RoleChoices.choices,
        default=RoleChoices.VECINO,
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDIENTE,
    )

    # Registro del aviso de privacidad mostrado al solicitar la cuenta.
    # No equivale por sí solo a un consentimiento para todas las finalidades.
    privacy_notice_version = models.CharField(max_length=40, blank=True, default="")
    privacy_notice_acknowledged_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "rut"
    REQUIRED_FIELDS = ["username", "email", "first_name", "last_name"]

    class Meta:
        verbose_name = "Residente"
        verbose_name_plural = "Residentes"

    def __str__(self):
        return f"{self.rut} - {self.get_full_name() or self.username}"
