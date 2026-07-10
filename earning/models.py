from django.db import models
from django.conf import settings


class Earning(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('available', 'Available'),
        ('paid',      'Paid'),
    ]

    writer         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    job            = models.ForeignKey(
        'work.Job',
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    gross_kes      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_kes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_kes        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.writer.full_name} — KES {self.net_kes} — {self.status}"


class Payout(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('processed', 'Processed'),
        ('failed',    'Failed'),
    ]

    writer       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    amount_kes   = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_number = models.CharField(max_length=15)
    mpesa_code   = models.CharField(max_length=20, blank=True)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.writer.full_name} — KES {self.amount_kes} — {self.status}"