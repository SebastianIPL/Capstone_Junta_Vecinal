from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class CommunitySpace(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Espacio")
    description = models.TextField(blank=True, verbose_name="Descripción y Normas de Uso")
    capacity = models.PositiveIntegerField(verbose_name="Capacidad Máxima (personas)")
    image = models.ImageField(
        upload_to='spaces/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Fotografía del Espacio"
    )
    is_active = models.BooleanField(default=True, verbose_name="Habilitado para Reservas")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Espacio Comunitario"
        verbose_name_plural = "Espacios Comunitarios"

    def __str__(self):
        return f"{self.name} (Capacidad: {self.capacity} personas)"


class SpaceReservation(models.Model):
    class StatusChoices(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de Aprobación'
        APROBADO = 'APROBADO', 'Aprobada'
        RECHAZADO = 'RECHAZADO', 'Rechazada'
        CANCELADA = 'CANCELADA', 'Cancelada por el Residente'

    space = models.ForeignKey(
        CommunitySpace,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name="Espacio Solicitado"
    )
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name="Residente Solicitante"
    )
    purpose = models.CharField(
        max_length=200,
        default="Uso general",
        verbose_name="Motivo de la Reserva"
    )
    start_time = models.DateTimeField(verbose_name="Fecha y Hora de Inicio")
    end_time = models.DateTimeField(verbose_name="Fecha y Hora de Término")
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDIENTE,
        verbose_name="Estado de la Solicitud"
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones de la Directiva"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Solicitud")

    class Meta:
        verbose_name = "Reserva de Espacio"
        verbose_name_plural = "Reservas de Espacios"
        ordering = ['-start_time']

    def clean(self):
        super().clean()
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("La hora de inicio debe ser anterior a la hora de término.")

            if self.start_time < timezone.now():
                raise ValidationError("No es posible reservar en fechas u horas pasadas.")

            conflicts = SpaceReservation.objects.filter(
                space=self.space,
                status__in=[self.StatusChoices.APROBADO, self.StatusChoices.PENDIENTE],
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )
            if self.pk:
                conflicts = conflicts.exclude(pk=self.pk)

            if conflicts.exists():
                raise ValidationError("El espacio ya tiene una solicitud pendiente o aprobada en ese rango horario.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva #{self.id} - {self.space.name} ({self.resident.rut})"