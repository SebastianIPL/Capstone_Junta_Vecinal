
import re
from urllib.parse import urlsplit, parse_qs

from django.conf import settings
from django.db import models


# ==========================================================
# CHAT COMUNITARIO - GRUPOS DE WHATSAPP
# ==========================================================

class WhatsAppGroup(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre del grupo"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )

    invite_link = models.URLField(
        max_length=500,
        verbose_name="Enlace de invitación"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Grupo activo"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Grupo de WhatsApp"
        verbose_name_plural = "Grupos de WhatsApp"

    def __str__(self):
        return self.name


# ==========================================================
# CÁMARAS COMUNITARIAS - CÁMARAS PÚBLICAS
# ==========================================================

class PublicCamera(models.Model):

    name = models.CharField(
        max_length=120,
        verbose_name="Nombre de la cámara"
    )

    location = models.CharField(
        max_length=200,
        verbose_name="Ubicación"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )

    source_name = models.CharField(
        max_length=120,
        verbose_name="Fuente o proveedor"
    )

    source_url = models.URLField(
        max_length=1000,
        verbose_name="URL pública de la transmisión"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Mostrar a los vecinos"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Cámara pública"
        verbose_name_plural = "Cámaras públicas"

    def __str__(self):
        return self.name

    # ------------------------------------------------------
    # GENERAR ENLACE INCRUSTABLE PARA YOUTUBE
    # ------------------------------------------------------

    @property
    def embed_url(self):

        """
        Convierte enlaces públicos de YouTube
        en URLs compatibles con iframe.

        Otras fuentes no se incrustan
        automáticamente y se abren externamente.
        """

        try:
            parsed = urlsplit(self.source_url)

            host = (parsed.hostname or "").lower()

            path = parsed.path.strip("/")

            video_id = None

            # Solo permitir HTTPS
            if parsed.scheme != "https":
                return ""

            # YouTube normal
            if host in (
                "youtube.com",
                "www.youtube.com",
                "m.youtube.com",
            ):

                if path == "watch":

                    video_id = parse_qs(
                        parsed.query
                    ).get("v", [None])[0]

                elif path.startswith(
                    ("live/", "embed/")
                ):

                    video_id = path.split("/")[-1]

            # YouTube corto
            elif host == "youtu.be":

                video_id = path

            # YouTube sin cookies
            elif host == "www.youtube-nocookie.com":

                if path.startswith("embed/"):

                    video_id = path.split("/")[-1]

            # Validar ID del video
            if video_id and re.fullmatch(
                r"[A-Za-z0-9_-]{11}",
                video_id
            ):

                return (
                    "https://www.youtube-nocookie.com/"
                    f"embed/{video_id}"
                )

        except (ValueError, AttributeError):

            pass

        return ""


# ==========================================================
# PORTÓN ELÉCTRICO - SIMULACIÓN
# ==========================================================

class Gate(models.Model):

    name = models.CharField(
        max_length=120,
        verbose_name="Nombre del portón"
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación"
    )

    phone_number = models.CharField(
        max_length=25,
        blank=True,
        verbose_name="Número telefónico de prueba"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Disponible para solicitudes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Portón"
        verbose_name_plural = "Portones"

    def __str__(self):
        return self.name


# ==========================================================
# SOLICITUDES DE ACCESO AL PORTÓN
# ==========================================================

class GateAccessRequest(models.Model):

    class Method(models.TextChoices):
        CALL = "CALL", "Llamada simulada"
        SMS = "SMS", "SMS simulado"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        APPROVED = "APPROVED", "Aprobada"
        REJECTED = "REJECTED", "Rechazada"

    gate = models.ForeignKey(
        Gate,
        on_delete=models.PROTECT,
        related_name="access_requests",
        verbose_name="Portón"
    )

    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="gate_requests",
        verbose_name="Solicitante"
    )

    method = models.CharField(
        max_length=10,
        choices=Method.choices,
        verbose_name="Método simulado"
    )

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Estado"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de solicitud"
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de resolución"
    )

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_gate_requests",
        verbose_name="Atendida por"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Solicitud de acceso"
        verbose_name_plural = "Solicitudes de acceso"

    def __str__(self):
        return (
            f"Solicitud #{self.pk} - "
            f"{self.gate.name} - {self.get_status_display()}"
        )

# ==========================================================
# CHAT PRIVADO ENTRE VECINOS Y GUARDIAS
# ==========================================================

class GuardConversation(models.Model):

    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="guard_conversations_as_resident"
    )

    guard = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="guard_conversations_as_guard"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["resident", "guard"],
                name="unique_resident_guard_chat"
            )
        ]

    def __str__(self):
        return (
            f"Chat #{self.pk}: "
            f"{self.resident} - {self.guard}"
        )


class GuardMessage(models.Model):

    conversation = models.ForeignKey(
        GuardConversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="guard_chat_messages"
    )

    content = models.TextField(
        max_length=2000,
        verbose_name="Mensaje"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Mensaje #{self.pk}"
