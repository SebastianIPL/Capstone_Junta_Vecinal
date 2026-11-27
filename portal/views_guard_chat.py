
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import GuardConversation, GuardMessage


# =====================================================
# PERMISOS
# =====================================================

def es_guardia(user):
    return (
        user.is_authenticated
        and user.is_active
        and user.groups.filter(name="Guardia").exists()
    )


def nombre_usuario(usuario):
    return usuario.get_full_name() or str(usuario)


# =====================================================
# BANDEJA DE CONVERSACIONES
# =====================================================

@login_required
def bandeja_guardia(request):

    User = get_user_model()
    usuario = request.user
    guardia = es_guardia(usuario)

    # El guardia ve las conversaciones que le enviaron.
    # El vecino ve únicamente sus conversaciones.
    if guardia:
        conversaciones = GuardConversation.objects.filter(
            guard=usuario
        )
    else:
        conversaciones = GuardConversation.objects.filter(
            resident=usuario
        )

    conversaciones = conversaciones.select_related(
        "resident", "guard"
    ).order_by("-updated_at")

    guardias_disponibles = User.objects.filter(
        is_active=True,
        groups__name="Guardia",
    ).exclude(
        pk=usuario.pk
    ).distinct().order_by("pk")

    return render(
        request,
        "portal/chat_guardia_bandeja.html",
        {
            "conversaciones": conversaciones,
            "guardias_disponibles": guardias_disponibles,
            "es_guardia": guardia,
        }
    )


# =====================================================
# INICIAR CHAT DESDE EL PORTAL DEL VECINO
# =====================================================

@login_required
@require_POST
def iniciar_chat_guardia(request):

    if es_guardia(request.user):
        messages.error(
            request,
            "Los guardias responden desde su bandeja."
        )
        return redirect("portal:chat_guardia_bandeja")

    User = get_user_model()

    guardia_id = request.POST.get("guardia_id")

    try:
        guardia = User.objects.get(
            pk=guardia_id,
            is_active=True,
            groups__name="Guardia"
        )
    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(
            request,
            "Selecciona un guardia disponible."
        )
        return redirect("portal:chat_guardia_bandeja")

    conversacion, _ = GuardConversation.objects.get_or_create(
        resident=request.user,
        guard=guardia
    )

    return redirect(
        "portal:chat_guardia_conversacion",
        pk=conversacion.pk
    )


# =====================================================
# VER UNA CONVERSACIÓN
# =====================================================

@login_required
def conversacion_guardia(request, pk):

    conversacion = get_object_or_404(
        GuardConversation.objects.select_related(
            "resident", "guard"
        ),
        pk=pk
    )

    usuario = request.user

    es_vecino_del_chat = (
        conversacion.resident_id == usuario.pk
    )

    es_guardia_del_chat = (
        conversacion.guard_id == usuario.pk
        and es_guardia(usuario)
    )

    if not (
        es_vecino_del_chat
        or es_guardia_del_chat
    ):
        return HttpResponseForbidden(
            "No tienes acceso a esta conversación."
        )

    mensajes_chat = conversacion.messages.select_related(
        "sender"
    ).all()

    guardia_disponible = (
        conversacion.guard.is_active
        and es_guardia(conversacion.guard)
    )

    return render(
        request,
        "portal/chat_guardia_conversacion.html",
        {
            "conversacion": conversacion,
            "mensajes_chat": mensajes_chat,
            "guardia_disponible": guardia_disponible,
        }
    )


# =====================================================
# ENVIAR MENSAJE
# =====================================================

@login_required
@require_POST
def enviar_mensaje_guardia(request, pk):

    conversacion = get_object_or_404(
        GuardConversation.objects.select_related("guard"),
        pk=pk
    )

    usuario = request.user

    puede_enviar = (
        conversacion.resident_id == usuario.pk
        or (
            conversacion.guard_id == usuario.pk
            and es_guardia(usuario)
        )
    )

    if not puede_enviar:
        return HttpResponseForbidden(
            "No puedes enviar mensajes en este chat."
        )

    if (
        not conversacion.guard.is_active
        or not es_guardia(conversacion.guard)
    ):
        messages.error(
            request,
            "Este guardia ya no está disponible."
        )
        return redirect(
            "portal:chat_guardia_conversacion",
            pk=pk
        )

    contenido = request.POST.get("content", "").strip()

    if not contenido or len(contenido) > 2000:
        messages.error(
            request,
            "El mensaje debe contener entre 1 y "
            "2000 caracteres."
        )
        return redirect(
            "portal:chat_guardia_conversacion",
            pk=pk
        )

    GuardMessage.objects.create(
        conversation=conversacion,
        sender=usuario,
        content=contenido,
    )

    conversacion.updated_at = timezone.now()
    conversacion.save(update_fields=["updated_at"])

    return redirect(
        "portal:chat_guardia_conversacion",
        pk=pk
    )
