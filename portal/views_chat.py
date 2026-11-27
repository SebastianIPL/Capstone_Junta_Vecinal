
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.views.decorators.http import require_POST

from .models import WhatsAppGroup
from .forms_chat import WhatsAppGroupForm


# =====================================================
# PERMISOS
# =====================================================

def puede_administrar_grupos(user):
    return (
        user.is_authenticated
        and (
            user.is_staff
            or user.is_superuser
            or getattr(user, "role", None) in (
                "DIRECTIVA",
                "ADMIN",
                "PRESIDENTE",
                "SECRETARIO",
                "TESORERO",
            )
        )
    )


def verificar_permisos(user):
    if not puede_administrar_grupos(user):
        raise PermissionDenied(
            "No tienes permiso para administrar grupos."
        )


# =====================================================
# VISTA PARA LOS VECINOS
# =====================================================

@login_required
def chat_groups(request):

    grupos = WhatsAppGroup.objects.filter(
        is_active=True
    )

    return render(
        request,
        "portal/chat.html",
        {
            "grupos": grupos,
        }
    )


# =====================================================
# LISTADO ADMINISTRATIVO DE GRUPOS
# =====================================================

@login_required
def gestionar_grupos(request):

    verificar_permisos(request.user)

    grupos = WhatsAppGroup.objects.all()

    return render(
        request,
        "portal/gestionar_grupos.html",
        {
            "grupos": grupos,
        }
    )


# =====================================================
# CREAR GRUPO
# =====================================================

@login_required
def crear_grupo(request):

    verificar_permisos(request.user)

    if request.method == "POST":

        form = WhatsAppGroupForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Grupo de WhatsApp creado correctamente."
            )

            return redirect("portal:gestionar_grupos")

    else:
        form = WhatsAppGroupForm()

    return render(
        request,
        "portal/formulario_grupo.html",
        {
            "form": form,
            "titulo": "Crear grupo de WhatsApp",
        }
    )


# =====================================================
# EDITAR GRUPO
# =====================================================

@login_required
def editar_grupo(request, pk):

    verificar_permisos(request.user)

    grupo = get_object_or_404(
        WhatsAppGroup,
        pk=pk
    )

    if request.method == "POST":

        form = WhatsAppGroupForm(
            request.POST,
            instance=grupo
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Grupo actualizado correctamente."
            )

            return redirect("portal:gestionar_grupos")

    else:
        form = WhatsAppGroupForm(
            instance=grupo
        )

    return render(
        request,
        "portal/formulario_grupo.html",
        {
            "form": form,
            "titulo": "Editar grupo de WhatsApp",
        }
    )


# =====================================================
# ELIMINAR GRUPO
# =====================================================

@login_required
@require_POST
def eliminar_grupo(request, pk):

    verificar_permisos(request.user)

    grupo = get_object_or_404(
        WhatsAppGroup,
        pk=pk
    )

    grupo.delete()

    messages.success(
        request,
        "Grupo eliminado correctamente."
    )

    return redirect("portal:gestionar_grupos")
