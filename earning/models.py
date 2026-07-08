from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class EscrowAccount(models.Model):
    STATUS_CHOICES = [
        ('awaiting_payment', 'Awaiting Payment'),
        ('held',             'In Escrow'),
        ('released',         'Released'),
        ('disputed',         'Disputed'),
        ('refunded',         'Refunded'),
    ]

    job                  = models.OneToOneField(
        'work.Job',
        on_delete=models.CASCADE,
        related_name='escrow'
    )
    client_payment_kes   = models.DecimalField(max_digits=10, decimal_places=2)
    commission_kes       = models.DecimalField(max_digits=10, decimal_places=2)
    writer_amount_kes    = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_code           = models.CharField(max_length=20, blank=True)
    status               = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='awaiting_payment'
    )
    auto_release_date    = models.DateTimeField(null=True, blank=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    released_at          = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.commission_kes:
            self.commission_kes    = self.client_payment_kes * 15 / 100
            self.writer_amount_kes = self.client_payment_kes - self.commission_kes
        if self.status == 'held' and not self.auto_release_date:
            self.auto_release_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Escrow: {self.job.title} — KES {self.client_payment_kes} — {self.status}"


class WriterEarning(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('available', 'Available'),
        ('withdrawn', 'Withdrawn'),
    ]

    writer            = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='writer_earnings'
    )
    job               = models.ForeignKey(
        'work.Job',
        on_delete=models.CASCADE,
        related_name='writer_earnings'
    )
    gross_amount_kes  = models.DecimalField(max_digits=10, decimal_places=2)
    commission_kes    = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount_kes    = models.DecimalField(max_digits=10, decimal_places=2)
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.writer.full_name} — KES {self.net_amount_kes} — {self.status}"


class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('processed', 'Processed'),
        ('failed',    'Failed'),
    ]

    MINIMUM_WITHDRAWAL_KES = 2500

    writer       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )
    amount_kes   = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_number = models.CharField(max_length=15)
    mpesa_code   = models.CharField(max_length=20, blank=True)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at   = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.writer.full_name} — KES {self.amount_kes} — {self.status}"
    