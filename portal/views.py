from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from certificates.models import CertificateRequest
from spaces.models import SpaceReservation
from residents.models import Resident


# --- Vistas Vecinales Generales ---

@login_required
def dashboard_view(request):
    return render(request, 'portal/dashboard.html')


@login_required
def mis_certificados_view(request):
    certificados = CertificateRequest.objects.filter(resident=request.user)
    return render(request, 'portal/mis_certificados.html', {'certificados': certificados})


@login_required
def camaras_view(request):
    return render(request, 'portal/camaras.html')


@login_required
def chat_view(request):
    return render(request, 'portal/chat.html')


# --- Panel Exclusivo de Directiva y Administradores ---

def is_directiva(user):
    return user.is_authenticated and (
        user.is_staff or getattr(user, 'role', '') in ['DIRECTIVA', 'PRESIDENTE', 'SECRETARIO', 'TESORERO']
    )


@user_passes_test(is_directiva, login_url='portal:dashboard')
def directiva_dashboard_view(request):
    # Pestaña activa por defecto: 'certificados' o 'reservas'
    active_tab = request.GET.get('tab', 'certificados')

    total_vecinos = Resident.objects.count()
    pendientes_cert = CertificateRequest.objects.filter(status=CertificateRequest.StatusChoices.PENDIENTE).count()
    total_aprobados_cert = CertificateRequest.objects.filter(status=CertificateRequest.StatusChoices.APROBADO).count()

    pendientes_reservas = SpaceReservation.objects.filter(status=SpaceReservation.StatusChoices.PENDIENTE).count()
    total_aprobadas_reservas = SpaceReservation.objects.filter(status=SpaceReservation.StatusChoices.APROBADO).count()

    solicitudes_cert = CertificateRequest.objects.select_related('resident').order_by('-created_at')[:30]
    solicitudes_reservas = SpaceReservation.objects.select_related('resident', 'space').order_by('-created_at')[:30]

    context = {
        'active_tab': active_tab,
        'total_vecinos': total_vecinos,
        'pendientes_cert': pendientes_cert,
        'total_aprobados_cert': total_aprobados_cert,
        'pendientes_reservas': pendientes_reservas,
        'total_aprobadas_reservas': total_aprobadas_reservas,
        'solicitudes_cert': solicitudes_cert,
        'solicitudes_reservas': solicitudes_reservas,
    }
    return render(request, 'portal/directiva_dashboard.html', context)


@user_passes_test(is_directiva, login_url='portal:dashboard')
def resolver_certificado(request, cert_id, action):
    cert = get_object_or_404(CertificateRequest, id=cert_id)
    if action == 'aprobar':
        cert.status = CertificateRequest.StatusChoices.APROBADO
        cert.issued_at = timezone.now()
        cert.save()
        messages.success(request, f"Certificado #{cert.id} aprobado exitosamente.")
    elif action == 'rechazar':
        cert.status = CertificateRequest.StatusChoices.RECHAZADO
        cert.save()
        messages.error(request, f"Certificado #{cert.id} ha sido rechazado.")

    return redirect('/directiva/?tab=certificados')


@user_passes_test(is_directiva, login_url='portal:dashboard')
def resolver_reserva(request, reserva_id, action):
    reserva = get_object_or_404(SpaceReservation, id=reserva_id)
    if action == 'aprobar':
        reserva.status = SpaceReservation.StatusChoices.APROBADO
        reserva.save()
        messages.success(request, f"Reserva #{reserva.id} para {reserva.space.name} aprobada.")
    elif action == 'rechazar':
        reserva.status = SpaceReservation.StatusChoices.RECHAZADO
        reserva.save()
        messages.error(request, f"Reserva #{reserva.id} ha sido rechazada.")

    return redirect('/directiva/?tab=reservas')