
from django.urls import path
from . import views

app_name = "bulletins"

urlpatterns = [
    path("", views.bulletin_list, name="list"),

    path(
        "nuevo/",
        views.bulletin_create,
        name="create"
    ),

    path(
        "editar/<int:pk>/",
        views.bulletin_edit,
        name="edit"
    ),

    path(
        "eliminar/<int:pk>/",
        views.bulletin_delete,
        name="delete"
    ),
]
