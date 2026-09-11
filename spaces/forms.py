from django import forms
from .models import CommunitySpace, SpaceReservation


class CommunitySpaceForm(forms.ModelForm):
    class Meta:
        model = CommunitySpace
        fields = ['name', 'capacity', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-emerald-600 focus:outline-none',
                'placeholder': 'Ej. Sede Social Principal, Multicancha Techada...'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-emerald-600 focus:outline-none',
                'placeholder': 'Aforo máximo de personas'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-emerald-600 focus:outline-none',
                'rows': 3,
                'placeholder': 'Detalles de equipamiento, normas de uso...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100'
            }),
        }
        labels = {
            'name': 'Nombre del Espacio',
            'capacity': 'Capacidad Máxima (personas)',
            'description': 'Descripción y Normas',
            'image': 'Fotografía del Lugar',
            'is_active': 'Habilitado inmediatamente para reservas',
        }


class SpaceReservationForm(forms.ModelForm):
    class Meta:
        model = SpaceReservation
        fields = ['space', 'purpose', 'start_time', 'end_time']
        widgets = {
            'space': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-emerald-600 focus:outline-none'
            }),
            'purpose': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-emerald-600 focus:outline-none',
                'placeholder': 'Ej. Taller vecinal, cumpleaños infantil...'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-emerald-600 focus:outline-none'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-emerald-600 focus:outline-none'
            }),
        }
        labels = {
            'space': 'Espacio Comunitario',
            'purpose': 'Motivo / Finalidad de Uso',
            'start_time': 'Fecha y Hora de Inicio',
            'end_time': 'Fecha y Hora de Término',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['space'].queryset = CommunitySpace.objects.filter(is_active=True)