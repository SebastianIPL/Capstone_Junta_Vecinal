
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views_cameras
from . import views_chat
from . import views_gate
from . import views_guards
from . import views_guard_chat

from .views import (
    dashboard_view,
    mis_certificados_view,
    camaras_view,
    chat_view,
    directiva_dashboard_view,
    resolver_certificado,
    resolver_reserva,
)

app_name = "portal"

urlpatterns = [

    # ===================================
    # DASHBOARD Y CERTIFICADOS
    # ===================================

    path(
        "",
        dashboard_view,
        name="dashboard"
    ),

    path(
        "mis-certificados/",
        mis_certificados_view,
        name="mis_certificados"
    ),

    # ===================================
    # CÁMARAS COMUNITARIAS
    # ===================================

    path(
        "camaras/",
        views_cameras.camaras_publicas,
        name="camaras"
    ),

    path(
        "directiva/camaras/",
        views_cameras.gestionar_camaras,
        name="gestionar_camaras"
    ),

    path(
        "directiva/camaras/nueva/",
        views_cameras.crear_camara,
        name="crear_camara"
    ),

    path(
        "directiva/camaras/editar/<int:pk>/",
        views_cameras.editar_camara,
        name="editar_camara"
    ),

    path(
        "directiva/camaras/eliminar/<int:pk>/",
        views_cameras.eliminar_camara,
        name="eliminar_camara"
    ),

    # ===================================
    # CHAT COMUNITARIO - WHATSAPP
    # ===================================

    path(
        "chat/",
        views_chat.chat_groups,
        name="chat"
    ),

    path(
        "directiva/grupos/",
        views_chat.gestionar_grupos,
        name="gestionar_grupos"
    ),

    path(
        "directiva/grupos/nuevo/",
        views_chat.crear_grupo,
        name="crear_grupo"
    ),

    path(
        "directiva/grupos/editar/<int:pk>/",
        views_chat.editar_grupo,
        name="editar_grupo"
    ),

    path(
        "directiva/grupos/eliminar/<int:pk>/",
        views_chat.eliminar_grupo,
        name="eliminar_grupo"
    ),

    # ===================================
    # PANEL DIRECTIVA
    # ===================================

    path(
        "directiva/",
        directiva_dashboard_view,
        name="directiva_dashboard"
    ),

    path(
        "directiva/certificados/<int:cert_id>/<str:action>/",
        resolver_certificado,
        name="resolver_certificado"
    ),

    path(
        "directiva/reservas/<int:reserva_id>/<str:action>/",
        resolver_reserva,
        name="resolver_reserva"
    ),

    # ===================================
    # AUTENTICACIÓN
    # ===================================

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="portal/login.html"
        ),
        name="login"
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout"
    ),

    # ===================================
    # PORTÓN ELÉCTRICO - SIMULACIÓN
    # ===================================

    path(
        "porton/",
        views_gate.porton_view,
        name="porton"
    ),

    path(
        "porton/solicitar/<int:gate_id>/",
        views_gate.solicitar_apertura,
        name="solicitar_apertura"
    ),

    path(
        "directiva/porton/",
        views_gate.gestionar_porton,
        name="gestionar_porton"
    ),

    path(
        "directiva/porton/resolver/<int:pk>/<str:accion>/",
        views_gate.resolver_solicitud,
        name="resolver_solicitud_porton"
    ),

    path(
        "directiva/porton/nuevo/",
        views_gate.crear_porton,
        name="crear_porton"
    ),

    path(
        "directiva/porton/editar/<int:pk>/",
        views_gate.editar_porton,
        name="editar_porton"
    ),

    # ===================================
    # ADMINISTRACIÓN DE GUARDIAS
    # ===================================

    path(
        "directiva/guardias/",
        views_guards.gestionar_guardias,
        name="gestionar_guardias"
    ),

    path(
        "directiva/guardias/asignar/",
        views_guards.asignar_guardia,
        name="asignar_guardia"
    ),

    path(
        "directiva/guardias/quitar/<int:user_id>/",
        views_guards.quitar_guardia,
        name="quitar_guardia"
    ),

    # ===================================
    # CHAT PRIVADO VECINO - GUARDIA
    # ===================================

    path(
        "guardia/chat/",
        views_guard_chat.bandeja_guardia,
        name="chat_guardia_bandeja"
    ),

    path(
        "guardia/chat/iniciar/",
        views_guard_chat.iniciar_chat_guardia,
        name="chat_guardia_iniciar"
    ),

    path(
        "guardia/chat/<int:pk>/",
        views_guard_chat.conversacion_guardia,
        name="chat_guardia_conversacion"
    ),

    path(
        "guardia/chat/<int:pk>/enviar/",
        views_guard_chat.enviar_mensaje_guardia,
        name="chat_guardia_enviar"
    ),

]
