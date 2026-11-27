from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .forms_registration import RegistroVecinoForm, PRIVACY_VERSION

Resident = get_user_model()


def es_directiva(user):
    return user.is_authenticated and user.is_active and (
        user.is_superuser or user.is_staff or
        getattr(user, 'role', '') in ('DIRECTIVA', 'ADMIN')
    )


def politica_privacidad(request):
    return render(request, 'residents/politica_privacidad.html', {'version': PRIVACY_VERSION})


@never_cache
def registro_vecino(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    form = RegistroVecinoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        # El modelo exige username único, aunque la autenticación utilice el RUT.
        username = f"vecino_{d['rut'].lower()}"
        try:
            with transaction.atomic():
                # Las cuentas nuevas quedan inactivas hasta la decisión de directiva.
                vecino = Resident(
                    username=username,
                    rut=d['rut'],
                    first_name=d['first_name'].strip(),
                    last_name=d['last_name'].strip(),
                    email=d['email'],
                    phone=d['phone'].strip(),
                    address=d['address'].strip(),
                    role='VECINO',
                    status='PENDIENTE',
                    is_active=False,
                    is_staff=False,
                    is_superuser=False,
                    privacy_notice_version=PRIVACY_VERSION,
                    privacy_notice_acknowledged_at=timezone.now(),
                )
                vecino.set_password(d['password1'])
                vecino.full_clean(exclude=['password'])
                vecino.save()
            return render(request, 'residents/registro_recibido.html')
        except (IntegrityError, ValidationError):
            # No exponer detalles internos a visitantes.
            form.add_error(None, 'No pudimos completar el registro. Comprueba que el RUT y correo no estén registrados.')

    return render(request, 'residents/registro.html', {'form': form})


@login_required
@never_cache
def solicitudes_registro(request):
    if not es_directiva(request.user):
        return HttpResponseForbidden('No tienes permisos para administrar registros.')
    pendientes = Resident.objects.filter(
        role='VECINO', status='PENDIENTE', is_active=False,
        is_staff=False, is_superuser=False,
    ).order_by('date_joined')
    return render(request, 'residents/solicitudes_registro.html', {'pendientes': pendientes})


@login_required
@require_POST
def resolver_registro(request, pk, accion):
    if not es_directiva(request.user):
        return HttpResponseForbidden('No tienes permisos para administrar registros.')
    if accion not in ('aprobar', 'rechazar'):
        return HttpResponseForbidden('Acción no permitida.')

    with transaction.atomic():
        vecino = get_object_or_404(
            Resident.objects.select_for_update(),
            pk=pk, role='VECINO', status='PENDIENTE',
            is_active=False, is_staff=False, is_superuser=False,
        )
        vecino.status = 'ACTIVO' if accion == 'aprobar' else 'RECHAZADO'
        vecino.is_active = accion == 'aprobar'
        vecino.save(update_fields=['status', 'is_active'])

    messages.success(request, 'Solicitud aprobada.' if accion == 'aprobar' else 'Solicitud rechazada.')
    return redirect('residents:solicitudes_registro')
