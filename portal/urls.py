from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    dashboard_view,
    mis_certificados_view,
    camaras_view,
    chat_view,
    directiva_dashboard_view,
    resolver_certificado,
    resolver_reserva,
)

app_name = 'portal'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('mis-certificados/', mis_certificados_view, name='mis_certificados'),
    path('camaras/', camaras_view, name='camaras'),
    path('chat/', chat_view, name='chat'),

    # Panel Directivo
    path('directiva/', directiva_dashboard_view, name='directiva_dashboard'),
    path('directiva/certificados/<int:cert_id>/<str:action>/', resolver_certificado, name='resolver_certificado'),
    path('directiva/reservas/<int:reserva_id>/<str:action>/', resolver_reserva, name='resolver_reserva'),

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='portal/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]