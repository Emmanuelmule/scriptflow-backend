from django.contrib import admin
from .models import Writer

@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'role', 'is_active', 'created_at']
    list_filter  = ['role', 'is_active']
    search_fields = ['email', 'full_name']