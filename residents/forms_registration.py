import re
from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

Resident = get_user_model()

PRIVACY_VERSION = '2026-11-26-v1'


def normalizar_rut(valor):
    return re.sub(r'[^0-9Kk]', '', valor or '').upper()


def rut_valido(rut):
    if len(rut) < 2 or len(rut) > 10 or not rut[:-1].isdigit():
        return False
    cuerpo, digito = rut[:-1], rut[-1]
    suma = sum(int(n) * (2 + (i % 6)) for i, n in enumerate(reversed(cuerpo)))
    resto = 11 - (suma % 11)
    esperado = '0' if resto == 11 else 'K' if resto == 10 else str(resto)
    return digito == esperado


class RegistroVecinoForm(forms.Form):
    first_name = forms.CharField(label='Nombres', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    rut = forms.CharField(label='RUT', max_length=12, help_text='Sin puntos; puede usar guion')
    email = forms.EmailField(label='Correo electrónico')
    phone = forms.CharField(label='Teléfono (opcional)', max_length=15, required=False)
    address = forms.CharField(label='Dirección de residencia', max_length=255)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repetir contraseña', widget=forms.PasswordInput)
    aviso_privacidad = forms.BooleanField(
        label='He leído la Política de Privacidad y entiendo el tratamiento de mis datos para tramitar mi registro.'
    )

    def clean_rut(self):
        rut = normalizar_rut(self.cleaned_data['rut'])
        if not rut_valido(rut):
            raise ValidationError('Ingresa un RUT chileno válido.')
        # Buscar la misma identidad con y sin puntos/guion, para bases anteriores.
        cuerpo, dv = rut[:-1], rut[-1]
        variantes = {rut, f'{cuerpo}-{dv}'}
        if Resident.objects.filter(rut__in=variantes).exists():
            raise ValidationError('Este RUT ya tiene una cuenta. Comunícate con la directiva.')
        return f'{cuerpo}-{dv}'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Resident.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este correo ya se encuentra registrado.')
        return email

    def clean(self):
        datos = super().clean()
        clave1, clave2 = datos.get('password1'), datos.get('password2')
        if clave1 and clave2 and clave1 != clave2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        if clave1:
            candidato = Resident(
                rut=datos.get('rut', ''),
                first_name=datos.get('first_name', ''),
                last_name=datos.get('last_name', ''),
                email=datos.get('email', ''),
            )
            try:
                password_validation.validate_password(clave1, candidato)
            except ValidationError as exc:
                self.add_error('password1', exc)
        return datos
