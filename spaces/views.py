from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import CommunitySpace, SpaceReservation
from .forms import SpaceReservationForm, CommunitySpaceForm


def is_directiva(user):
    return user.is_authenticated and (
        user.is_staff or getattr(user, 'role', '') in ['DIRECTIVA', 'PRESIDENTE', 'SECRETARIO', 'TESORERO']
    )


@login_required
def mis_reservas_view(request):
    reservas = SpaceReservation.objects.filter(resident=request.user).select_related('space')
    espacios = CommunitySpace.objects.filter(is_active=True)
    return render(request, 'spaces/mis_reservas.html', {
        'reservas': reservas,
        'espacios': espacios
    })


@login_required
def solicitar_reserva_view(request):
    if request.method == 'POST':
        form = SpaceReservationForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.resident = request.user
            try:
                reserva.save()
                messages.success(request, "Tu solicitud de reserva fue enviada. Queda en revisión directiva.")
                return redirect('spaces:mis_reservas')
            except Exception as e:
                messages.error(request, f"Error al validar reserva: {e}")
    else:
        space_id = request.GET.get('space_id')
        initial_data = {'space': space_id} if space_id else {}
        form = SpaceReservationForm(initial=initial_data)

    return render(request, 'spaces/solicitar_reserva.html', {'form': form})


@user_passes_test(is_directiva, login_url='spaces:mis_reservas')
def crear_espacio_view(request):
    if request.method == 'POST':
        form = CommunitySpaceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Nuevo recinto comunitario registrado con éxito.")
            return redirect('spaces:mis_reservas')
    else:
        form = CommunitySpaceForm()

    return render(request, 'spaces/crear_espacio.html', {'form': form})