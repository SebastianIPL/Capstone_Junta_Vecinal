
from urllib.parse import urlsplit
import ipaddress

from django import forms
from .models import PublicCamera


class PublicCameraForm(forms.ModelForm):

    class Meta:
        model = PublicCamera

        fields = [
            "name",
            "location",
            "description",
            "source_name",
            "source_url",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full border border-slate-300 rounded-xl px-4 py-3",
                "placeholder": "Ej: Cámara Plaza Central",
            }),

            "location": forms.TextInput(attrs={
                "class": "w-full border border-slate-300 rounded-xl px-4 py-3",
                "placeholder": "Ej: Viña del Mar",
            }),

            "description": forms.Textarea(attrs={
                "class": "w-full border border-slate-300 rounded-xl px-4 py-3",
                "rows": 4,
                "placeholder": "Descripción de la cámara",
            }),

            "source_name": forms.TextInput(attrs={
                "class": "w-full border border-slate-300 rounded-xl px-4 py-3",
                "placeholder": "Ej: Canal oficial de YouTube",
            }),

            "source_url": forms.URLInput(attrs={
                "class": "w-full border border-slate-300 rounded-xl px-4 py-3",
                "placeholder": "https://www.youtube.com/watch?v=...",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "w-5 h-5 rounded border-slate-300",
            }),
        }

    def clean_source_url(self):
        url = self.cleaned_data["source_url"].strip()

        try:
            parsed = urlsplit(url)
            hostname = (parsed.hostname or "").lower()
            port = parsed.port
        except ValueError:
            raise forms.ValidationError(
                "El enlace ingresado no es válido."
            )

        if (
            parsed.scheme != "https"
            or not hostname
            or port is not None
            or parsed.username is not None
            or parsed.password is not None
            or hostname == "localhost"
            or hostname.endswith(".localhost")
            or hostname.endswith(".local")
        ):
            raise forms.ValidationError(
                "Debes ingresar un enlace HTTPS público."
            )

        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            if not ip.is_global:
                raise forms.ValidationError(
                    "No se permiten direcciones IP privadas."
                )

        return url
