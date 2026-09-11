from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Resident


@admin.register(Resident)
class ResidentAdmin(UserAdmin):
    list_display = ('rut', 'get_full_name', 'email', 'address', 'role', 'status_badge', 'is_staff')
    list_filter = ('role', 'status', 'is_staff')
    search_fields = ('rut', 'username', 'first_name', 'last_name', 'email', 'address')
    ordering = ('rut',)

    fieldsets = UserAdmin.fieldsets + (
        ('Información Territorial y Contacto', {
            'fields': ('rut', 'phone', 'address', 'birth_date', 'role', 'status')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Territorial y Contacto', {
            'fields': ('rut', 'phone', 'address', 'birth_date', 'role', 'status')
        }),
    )

    @admin.display(description="Estado Registro")
    def status_badge(self, obj):
        colores = {
            'ACTIVO': '#10B981',
            'PENDIENTE': '#F59E0B',
            'RECHAZADO': '#EF4444',
        }
        color = colores.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )