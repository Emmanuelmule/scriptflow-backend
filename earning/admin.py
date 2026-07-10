from django.contrib import admin
from .models import Earning, Payout

@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ['writer', 'job', 'gross_kes', 'commission_kes', 'net_kes', 'status', 'created_at']
    list_filter  = ['status']

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['writer', 'amount_kes', 'mpesa_number', 'status', 'created_at']
    list_filter  = ['status']