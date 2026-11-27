
from django.contrib import admin
from .models import Bulletin


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'priority',
        'author',
        'created_at',
        'expires_at',
        'is_published',
    )

    list_filter = (
        'priority',
        'is_published',
        'created_at',
    )

    search_fields = (
        'title',
        'content',
    )

    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user

        super().save_model(request, obj, form, change)
