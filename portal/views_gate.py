
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Gate, GateAccessRequest
from .forms_gate import GateForm


# =====================================================
# PERMISOS
# =====================================================

def puede_atender_porton(user):
    if not user.is_authenticated:
        return False

    es_guardia = user.groups.filter(
        name="Guardia"
    ).exists()

    return (
        user.is_staff
        or user.is_superuser
        or getattr(user, "role", None) in (
            "DIRECTIVA",
            "ADMIN",
            "GUARDIA",
        )
        or es_guardia
    )


def puede_configurar_porton(user):
    if not user.is_authenticated:
        return False

    return (
        user.is_staff
        or user.is_superuser
        or getattr(user, "role", None) in (
            "DIRECTIVA",
            "ADMIN",
        )
    )


def verificar_guardia(user):
    if not puede_atender_porton(user):
        raise PermissionDenied(
            "No tienes permiso para atender solicitudes."
        )


def verificar_directiva(user):
    if not puede_configurar_porton(user):
        raise PermissionDenied(
            "No tienes permiso para configurar portones."
        )


# =====================================================
# PORTAL DEL VECINO
# =====================================================

@login_required
def porton_view(request):

    portones = Gate.objects.filter(
        is_active=True
    )

    solicitudes = (
        GateAccessRequest.objects
        .filter(resident=request.user)
        .select_related("gate", "processed_by")[:20]
    )

    return render(
        request,
        "portal/porton.html",
        {
            "portones": portones,
            "solicitudes": solicitudes,
            "puede_atender": puede_atender_porton(
                request.user
            ),
        }
    )


# =====================================================
# CREAR SOLICITUD SIMULADA
# =====================================================

@login_required
@require_POST
def solicitar_apertura(request, gate_id):

    porton = get_object_or_404(
        Gate,
        pk=gate_id,
        is_active=True
    )

    metodo = request.POST.get("method", "").upper()

    metodos_validos = (
        GateAccessRequest.Method.CALL,
        GateAccessRequest.Method.SMS,
    )

    if metodo not in metodos_validos:
        messages.error(
            request,
            "Método de solicitud no válido."
        )
        return redirect("portal:porton")

    # Evitar múltiples solicitudes pendientes
    # para el mismo usuario y portón.
    existe_pendiente = (
        GateAccessRequest.objects
        .filter(
            gate=porton,
            resident=request.user,
            status=GateAccessRequest.Status.PENDING,
        )
        .exists()
    )

    if existe_pendiente:
        messages.warning(
            request,
            "Ya tienes una solicitud pendiente "
            "para este portón."
        )
        return redirect("portal:porton")

    solicitud = GateAccessRequest.objects.create(
        gate=porton,
        resident=request.user,
        method=metodo,
    )

    messages.success(
        request,
        f"Solicitud simulada #{solicitud.pk} registrada. "
        "No se envió ninguna llamada ni SMS real."
    )

    return redirect("portal:porton")


# =====================================================
# PANEL GUARDIA / DIRECTIVA
# =====================================================

@login_required
def gestionar_porton(request):

    verificar_guardia(request.user)

    pendientes = (
        GateAccessRequest.objects
        .filter(
            status=GateAccessRequest.Status.PENDING
        )
        .select_related("resident", "gate")
        .order_by("created_at")
    )

    historial = (
        GateAccessRequest.objects
        .exclude(
            status=GateAccessRequest.Status.PENDING
        )
        .select_related(
            "resident",
            "gate",
            "processed_by",
        )[:30]
    )

    portones = Gate.objects.all()

    return render(
        request,
        "portal/gestionar_porton.html",
        {
            "pendientes": pendientes,
            "historial": historial,
            "portones": portones,
            "total_pendientes": pendientes.count(),
            "puede_configurar": puede_configurar_porton(
                request.user
            ),
        }
    )


# =====================================================
# RESOLVER SOLICITUD
# =====================================================

@login_required
@require_POST
def resolver_solicitud(request, pk, accion):

    verificar_guardia(request.user)

    if accion not in ("aprobar", "rechazar"):
        messages.error(
            request,
            "Acción no válida."
        )
        return redirect("portal:gestionar_porton")

    with transaction.atomic():

        solicitud = get_object_or_404(
            GateAccessRequest.objects.select_for_update(),
            pk=pk
        )

        if solicitud.status != (
            GateAccessRequest.Status.PENDING
        ):
            messages.warning(
                request,
                "Esta solicitud ya fue gestionada."
            )
            return redirect("portal:gestionar_porton")

        if accion == "aprobar":
            solicitud.status = (
                GateAccessRequest.Status.APPROVED
            )
        else:
            solicitud.status = (
                GateAccessRequest.Status.REJECTED
            )

        solicitud.processed_by = request.user
        solicitud.processed_at = timezone.now()

        solicitud.save(
            update_fields=[
                "status",
                "processed_by",
                "processed_at",
            ]
        )

    messages.success(
        request,
        "Solicitud gestionada correctamente. "
        "No se activó ningún dispositivo físico."
    )

    return redirect("portal:gestionar_porton")


# =====================================================
# CREAR PORTÓN
# =====================================================

@login_required
def crear_porton(request):

    verificar_directiva(request.user)

    if request.method == "POST":
        form = GateForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Portón de simulación creado correctamente."
            )

            return redirect("portal:gestionar_porton")
    else:
        form = GateForm()

    return render(
        request,
        "portal/formulario_porton.html",
        {
            "form": form,
            "titulo": "Agregar portón",
        }
    )


# =====================================================
# EDITAR PORTÓN
# =====================================================

@login_required
def editar_porton(request, pk):

    verificar_directiva(request.user)

    porton = get_object_or_404(
        Gate,
        pk=pk
    )

    if request.method == "POST":
        form = GateForm(
            request.POST,
            instance=porton
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Portón actualizado correctamente."
            )

            return redirect("portal:gestionar_porton")
    else:
        form = GateForm(instance=porton)

    return render(
        request,
        "portal/formulario_porton.html",
        {
            "form": form,
            "titulo": "Editar portón",
        }
    )
