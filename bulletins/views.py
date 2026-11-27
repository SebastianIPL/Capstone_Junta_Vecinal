
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Bulletin
from .forms import BulletinForm


# ============================================================
# PERMISOS DE ADMINISTRACIÓN
# ============================================================

def puede_administrar(user):
    """
    Verifica si el usuario tiene permisos para administrar
    los avisos comunitarios.
    """
    return (
        user.is_authenticated
        and (
            user.is_staff
            or user.is_superuser
            or getattr(user, "role", None) in ("DIRECTIVA", "ADMIN")
        )
    )


def verificar_directiva(request):
    """
    Impide que los vecinos comunes puedan crear,
    editar o eliminar avisos.
    """
    if not puede_administrar(request.user):
        raise PermissionDenied(
            "No tienes permisos para administrar avisos."
        )


# ============================================================
# LISTADO DE AVISOS
# ============================================================

@login_required
def bulletin_list(request):
    """
    Los vecinos ven únicamente avisos publicados y vigentes.

    La directiva puede visualizar todos los avisos,
    incluidos borradores y anuncios vencidos.
    """

    ahora = timezone.now()

    if puede_administrar(request.user):

        avisos = Bulletin.objects.all().order_by(
            "-created_at"
        )

    else:

        avisos = Bulletin.objects.filter(
            is_published=True
        ).filter(
            Q(expires_at__isnull=True)
            | Q(expires_at__gt=ahora)
        ).order_by(
            "-created_at"
        )

    return render(request, "bulletins/list.html", {
        "bulletins": avisos,
        "puede_administrar": puede_administrar(request.user),
        "ahora": ahora,
    })


# ============================================================
# CREAR ANUNCIO CON IMAGEN
# ============================================================

@login_required
def bulletin_create(request):
    """
    Permite a la directiva crear avisos con
    título, contenido, prioridad e imagen opcional.
    """

    verificar_directiva(request)

    if request.method == "POST":

        # request.FILES recibe la imagen del formulario
        form = BulletinForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            aviso = form.save(commit=False)

            # Registrar automáticamente al autor
            aviso.author = request.user

            aviso.save()

            messages.success(
                request,
                "Aviso creado correctamente."
            )

            return redirect("bulletins:list")

    else:

        form = BulletinForm()

    return render(request, "bulletins/form.html", {
        "form": form,
        "titulo": "Publicar nuevo aviso",
    })


# ============================================================
# EDITAR ANUNCIO Y CAMBIAR IMAGEN
# ============================================================

@login_required
def bulletin_edit(request, pk):
    """
    Permite modificar un aviso existente.

    También permite reemplazar o quitar su imagen.
    """

    verificar_directiva(request)

    aviso = get_object_or_404(
        Bulletin,
        pk=pk
    )

    if request.method == "POST":

        # request.FILES permite actualizar la imagen
        form = BulletinForm(
            request.POST,
            request.FILES,
            instance=aviso
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Aviso actualizado correctamente."
            )

            return redirect("bulletins:list")

    else:

        form = BulletinForm(
            instance=aviso
        )

    return render(request, "bulletins/form.html", {
        "form": form,
        "titulo": "Editar aviso",
        "aviso": aviso,
    })


# ============================================================
# ELIMINAR ANUNCIO
# ============================================================

@login_required
@require_POST
def bulletin_delete(request, pk):
    """
    Elimina un aviso comunitario.

    Solamente permite solicitudes POST y usuarios
    autorizados.
    """

    verificar_directiva(request)

    aviso = get_object_or_404(
        Bulletin,
        pk=pk
    )

    aviso.delete()

    messages.success(
        request,
        "Aviso eliminado correctamente."
    )

    return redirect("bulletins:list")
