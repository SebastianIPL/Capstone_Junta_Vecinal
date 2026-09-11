from django import forms
from .models import CertificateRequest


class CertificateRequestForm(forms.ModelForm):
    class Meta:
        model = CertificateRequest
        fields = ['purpose', 'address_proof']
        widgets = {
            'purpose': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none',
                'placeholder': 'Ej. Postulación a subsidio habitacional, matrícula escolar, etc.'
            }),
            'address_proof': forms.ClearableFileInput(attrs={
                'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),
        }
        labels = {
            'purpose': 'Motivo o Finalidad del Trámite',
            'address_proof': 'Comprobante de Domicilio (Boleta de servicio, cuenta básica, etc.)',
        }