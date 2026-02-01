from django.contrib import admin
from .models import Paste


@admin.register(Paste)
class PasteAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'expires_at', 'max_views', 'view_count')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('id', 'content')
    readonly_fields = ('id', 'created_at', 'view_count')
