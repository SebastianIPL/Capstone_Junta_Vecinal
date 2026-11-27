
import re
from urllib.parse import urlsplit

from django import forms
from .models import WhatsAppGroup


class WhatsAppGroupForm(forms.ModelForm):

    class Meta:
        model = WhatsAppGroup

        fields = [
            "name",
            "description",
            "invite_link",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": (
                    "w-full border border-slate-300 "
                    "rounded-xl px-4 py-3"
                ),
                "placeholder": "Ej: Grupo General",
            }),

            "description": forms.Textarea(attrs={
                "class": (
                    "w-full border border-slate-300 "
                    "rounded-xl px-4 py-3"
                ),
                "rows": 4,
                "placeholder": (
                    "¿Cuál es el propósito del grupo?"
                ),
            }),

            "invite_link": forms.URLInput(attrs={
                "class": (
                    "w-full border border-slate-300 "
                    "rounded-xl px-4 py-3"
                ),
                "placeholder": (
                    "https://chat.whatsapp.com/..."
                ),
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": (
                    "w-5 h-5 rounded border-slate-300"
                ),
            }),
        }

    def clean_invite_link(self):
        link = self.cleaned_data["invite_link"].strip()

        try:
            parsed = urlsplit(link)
            port = parsed.port
        except ValueError:
            raise forms.ValidationError(
                "El enlace de WhatsApp no es válido."
            )

        code = parsed.path.strip("/")

        if (
            parsed.scheme != "https"
            or parsed.hostname != "chat.whatsapp.com"
            or port is not None
            or parsed.username is not None
            or parsed.password is not None
            or not re.fullmatch(
                r"[A-Za-z0-9_-]+", code
            )
        ):
            raise forms.ValidationError(
                "Debes ingresar un enlace de invitación "
                "válido de chat.whatsapp.com."
            )

        # Guarda el enlace sin parámetros adicionales.
        return f"https://chat.whatsapp.com/{code}"
