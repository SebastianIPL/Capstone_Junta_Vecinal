from django.contrib import admin
from django.utils.html import format_html
from .models import CommunitySpace, SpaceReservation


@admin.register(CommunitySpace)
class CommunitySpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_active', 'image_preview', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

    @admin.display(description="Foto")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 45px; height: 35px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url
            )
        return "Sin foto"


@admin.register(SpaceReservation)
class SpaceReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'space', 'resident', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'space')
    search_fields = ('resident__rut', 'resident__first_name', 'purpose')