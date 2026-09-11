import uuid
from django.db import models
from django.conf import settings


class CertificateRequest(models.Model):
    class StatusChoices(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de Revisión'
        APROBADO = 'APROBADO', 'Aprobado'
        RECHAZADO = 'RECHAZADO', 'Rechazado'

    # Identificador único e infalsificable para verificación pública y QR
    verification_code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Código de Verificación"
    )
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="Residente"
    )
    purpose = models.CharField(
        max_length=200,
        verbose_name="Finalidad del Trámite (ej: Licencia de conducir, subsidio)"
    )
    address_proof = models.FileField(
        upload_to='certificates/proofs/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Comprobante de Domicilio (Opcional)"
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDIENTE,
        verbose_name="Estado"
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motivo de Rechazo (si aplica)"
    )
    issued_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de Emisión"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Solicitud"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )

    class Meta:
        verbose_name = "Solicitud de Certificado"
        verbose_name_plural = "Solicitudes de Certificados"
        ordering = ['-created_at']

    def __str__(self):
        return f"Certificado #{self.id} - {self.resident.rut} ({self.get_status_display()})"