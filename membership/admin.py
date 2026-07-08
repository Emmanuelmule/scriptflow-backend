from django.contrib import admin
from .models import CreditPackage, CreditTransaction, WriterCredits

@admin.register(CreditPackage)
class CreditPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'credits', 'price_kes', 'is_active']

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['writer', 'type', 'credits', 'description', 'created_at']

@admin.register(WriterCredits)
class WriterCreditsAdmin(admin.ModelAdmin):
    list_display = ['writer', 'balance']