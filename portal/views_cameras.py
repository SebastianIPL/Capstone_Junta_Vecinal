
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import PublicCamera
from .forms_cameras import PublicCameraForm


def puede_administrar_camaras(user):
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
    if not puede_administrar_camaras(user):
        raise PermissionDenied(
            "No tienes permiso para administrar cámaras."
        )


@login_required
def camaras_publicas(request):
    camaras = PublicCamera.objects.filter(is_active=True)

    return render(
        request,
        "portal/camaras.html",
        {"camaras": camaras}
    )


@login_required
def gestionar_camaras(request):
    verificar_permisos(request.user)

    camaras = PublicCamera.objects.all()

    return render(
        request,
        "portal/gestionar_camaras.html",
        {"camaras": camaras}
    )


@login_required
def crear_camara(request):
    verificar_permisos(request.user)

    if request.method == "POST":
        form = PublicCameraForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Cámara agregada correctamente."
            )
            return redirect("portal:gestionar_camaras")
    else:
        form = PublicCameraForm()

    return render(
        request,
        "portal/formulario_camara.html",
        {
            "form": form,
            "titulo": "Agregar cámara pública",
        }
    )


@login_required
def editar_camara(request, pk):
    verificar_permisos(request.user)

    camara = get_object_or_404(PublicCamera, pk=pk)

    if request.method == "POST":
        form = PublicCameraForm(
            request.POST,
            instance=camara
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Cámara actualizada correctamente."
            )
            return redirect("portal:gestionar_camaras")
    else:
        form = PublicCameraForm(instance=camara)

    return render(
        request,
        "portal/formulario_camara.html",
        {
            "form": form,
            "titulo": "Editar cámara pública",
        }
    )


@login_required
@require_POST
def eliminar_camara(request, pk):
    verificar_permisos(request.user)

    camara = get_object_or_404(PublicCamera, pk=pk)
    camara.delete()

    messages.success(
        request,
        "Cámara eliminada del portal."
    )

    return redirect("portal:gestionar_camaras")
