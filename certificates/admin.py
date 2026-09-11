from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import CertificateRequest


@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'resident_info', 'purpose', 'status_badge', 'created_at', 'pdf_link')
    list_filter = ('status', 'created_at')
    search_fields = ('resident__rut', 'resident__first_name', 'resident__last_name', 'purpose')
    readonly_fields = ('verification_code', 'created_at', 'updated_at')
    actions = ['approve_selected', 'reject_selected']

    @admin.display(description="Vecino Solicitante")
    def resident_info(self, obj):
        return f"{obj.resident.rut} - {obj.resident.get_full_name() or obj.resident.username}"

    @admin.display(description="Estado")
    def status_badge(self, obj):
        colores = {
            'APROBADO': '#10B981',  # Verde
            'PENDIENTE': '#F59E0B', # Ámbar
            'RECHAZADO': '#EF4444', # Rojo
        }
        color = colores.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )

    @admin.display(description="Documento")
    def pdf_link(self, obj):
        if obj.status == CertificateRequest.StatusChoices.APROBADO:
            return format_html(
                '<a href="/certificates/download/{}/" target="_blank" style="color: #2563EB; font-weight: bold;">Descargar PDF</a>',
                obj.id
            )
        return "-"

    @admin.action(description="Aprobar certificados seleccionados")
    def approve_selected(self, request, queryset):
        queryset.update(status=CertificateRequest.StatusChoices.APROBADO, issued_at=timezone.now())

    @admin.action(description="Rechazar certificados seleccionados")
    def reject_selected(self, request, queryset):
        queryset.update(status=CertificateRequest.StatusChoices.RECHAZADO)