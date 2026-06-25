from django.db import models
from django.conf import settings


class Earning(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('available', 'Available'),
        ('paid',      'Paid'),
    ]

    writer     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    job        = models.ForeignKey(
        'work.Job',
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    amount_usd = models.DecimalField(max_digits=8, decimal_places=2)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.writer.full_name} — ${self.amount_usd} — {self.status}"


class Payout(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('processed', 'Processed'),
        ('failed',    'Failed'),
    ]

    METHOD_CHOICES = [
        ('mpesa',    'M-Pesa'),
        ('payoneer', 'Payoneer'),
        ('grey',     'Grey'),
    ]

    writer        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    amount_usd    = models.DecimalField(max_digits=8,  decimal_places=2)
    amount_kes    = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    method        = models.CharField(max_length=10, choices=METHOD_CHOICES)
    reference     = models.CharField(max_length=100, blank=True)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    processed_at  = models.DateTimeField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']