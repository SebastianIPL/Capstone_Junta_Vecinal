
from django.urls import path
from . import views_registration

app_name = "residents"

urlpatterns = [
    path(
        "registro/",
        views_registration.registro_vecino,
        name="registro"
    ),

    path(
        "privacidad/",
        views_registration.politica_privacidad,
        name="privacidad"
    ),

    path(
        "solicitudes/",
        views_registration.solicitudes_registro,
        name="solicitudes_registro"
    ),

    path(
        "solicitudes/<int:pk>/<str:accion>/",
        views_registration.resolver_registro,
        name="resolver_registro"
    ),
]
