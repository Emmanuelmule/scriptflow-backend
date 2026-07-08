from django.contrib import admin
from .models import EscrowAccount, WriterEarning, Withdrawal


@admin.register(EscrowAccount)
class EscrowAdmin(admin.ModelAdmin):
    list_display = ['job', 'client_payment_kes', 'commission_kes', 'writer_amount_kes', 'status']
    list_filter  = ['status']


@admin.register(WriterEarning)
class WriterEarningAdmin(admin.ModelAdmin):
    list_display = ['writer', 'job', 'gross_amount_kes', 'commission_kes', 'net_amount_kes', 'status']
    list_filter  = ['status']


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['writer', 'amount_kes', 'mpesa_number', 'status', 'created_at']
    list_filter  = ['status']