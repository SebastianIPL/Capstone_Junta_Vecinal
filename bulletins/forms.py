
from django import forms
from .models import Bulletin


class BulletinForm(forms.ModelForm):
    expires_at = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "w-full border border-slate-300 rounded-lg p-3"
            }
        ),
        label="Fecha de vencimiento"
    )

    class Meta:
        model = Bulletin

        fields = [
            "title",
            "content",
            "image",
            "priority",
            "expires_at",
            "is_published",
]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full border border-slate-300 rounded-lg p-3",
                "placeholder": "Título del anuncio"
            }),

            "content": forms.Textarea(attrs={
                "class": "w-full border border-slate-300 rounded-lg p-3",
                "rows": 6,
                "placeholder": "Escribe el comunicado..."
            }),

            "priority": forms.Select(attrs={
                "class": "w-full border border-slate-300 rounded-lg p-3"
            }),

            "is_published": forms.CheckboxInput(attrs={
                "class": "h-5 w-5 accent-blue-700"
            }),
        }
