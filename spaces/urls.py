from django.urls import path
from .views import mis_reservas_view, solicitar_reserva_view, crear_espacio_view

app_name = 'spaces'

urlpatterns = [
    path('', mis_reservas_view, name='mis_reservas'),
    path('solicitar/', solicitar_reserva_view, name='solicitar'),
    path('nuevo/', crear_espacio_view, name='crear_espacio'),
]