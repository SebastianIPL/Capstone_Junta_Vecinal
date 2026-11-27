
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.views.decorators.http import require_POST

from .views_gate import puede_configurar_porton


# =============================================
# PERMISOS
# =============================================

def verificar_directiva(user):
    if not puede_configurar_porton(user):
        raise PermissionDenied(
            "No tienes permiso para administrar guardias."
        )


# =============================================
# LISTAR GUARDIAS
# =============================================

@login_required
def gestionar_guardias(request):

    verificar_directiva(request.user)

    User = get_user_model()

    guardias = User.objects.filter(
        groups__name="Guardia"
    ).distinct()

    candidatos = (
        User.objects
        .filter(is_active=True)
        .exclude(groups__name="Guardia")
        .exclude(is_superuser=True)
        .order_by("pk")
    )

    return render(
        request,
        "portal/gestionar_guardias.html",
        {
            "guardias": guardias,
            "candidatos": candidatos,
        }
    )


# =============================================
# ASIGNAR GUARDIA
# =============================================

@login_required
@require_POST
def asignar_guardia(request):

    verificar_directiva(request.user)

    User = get_user_model()

    usuario = get_object_or_404(
        User,
        pk=request.POST.get("user_id"),
        is_active=True,
        is_superuser=False,
    )

    with transaction.atomic():

        grupo, _ = Group.objects.get_or_create(
            name="Guardia"
        )

        usuario.groups.add(grupo)

    messages.success(
        request,
        "Guardia asignado correctamente."
    )

    return redirect("portal:gestionar_guardias")


# =============================================
# QUITAR GUARDIA
# =============================================

@login_required
@require_POST
def quitar_guardia(request, user_id):

    verificar_directiva(request.user)

    User = get_user_model()

    usuario = get_object_or_404(
        User,
        pk=user_id
    )

    grupo = Group.objects.filter(
        name="Guardia"
    ).first()

    if grupo:
        usuario.groups.remove(grupo)

    messages.success(
        request,
        "Cargo de guardia retirado correctamente."
    )

    return redirect("portal:gestionar_guardias")
