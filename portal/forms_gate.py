
from django import forms
from .models import Gate


FIELD_CLASS = (
    "w-full border border-slate-300 rounded-xl "
    "px-4 py-3 focus:outline-none "
    "focus:ring-2 focus:ring-blue-500"
)


class GateForm(forms.ModelForm):

    class Meta:
        model = Gate

        fields = [
            "name",
            "location",
            "phone_number",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": FIELD_CLASS,
                "placeholder": "Ej: Portón Principal",
            }),

            "location": forms.TextInput(attrs={
                "class": FIELD_CLASS,
                "placeholder": "Ej: Acceso norte",
            }),

            "phone_number": forms.TextInput(attrs={
                "class": FIELD_CLASS,
                "placeholder": "+56 9 0000 0000",
            }),

            "description": forms.Textarea(attrs={
                "class": FIELD_CLASS,
                "rows": 3,
                "placeholder": "Información del acceso",
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "w-5 h-5 rounded border-slate-300",
            }),
        }
