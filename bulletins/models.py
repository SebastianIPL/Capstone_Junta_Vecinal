
from django.db import models
from django.conf import settings
from django.utils import timezone


class Bulletin(models.Model):
    image = models.ImageField(
    upload_to='bulletins/',
    blank=True,
    null=True,
    verbose_name='Imagen del anuncio'
)

    PRIORITY_CHOICES = [
        ('INFO', 'Informativo'),
        ('URGENT', 'Urgente'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )

    content = models.TextField(
        verbose_name='Contenido'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='INFO',
        verbose_name='Prioridad'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Autor'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de vencimiento'
    )

    is_published = models.BooleanField(
        default=True,
        verbose_name='Publicado'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Aviso comunitario'
        verbose_name_plural = 'Avisos comunitarios'

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return (
            self.is_published
            and (
                self.expires_at is None
                or self.expires_at > timezone.now()
            )
        )
