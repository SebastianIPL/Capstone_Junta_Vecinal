from django.urls import path
from .views import download_certificate_pdf, verify_certificate_view, create_certificate_request

app_name = 'certificates'

urlpatterns = [
    path('solicitar/', create_certificate_request, name='solicitar'),
    path('download/<int:certificate_id>/', download_certificate_pdf, name='download_pdf'),
    path('verify/<uuid:code>/', verify_certificate_view, name='verify_public'),
]