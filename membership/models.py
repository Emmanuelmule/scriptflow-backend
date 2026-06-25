from django.db import models
from django.conf import settings

TIER_CHOICES = [
    ('basic',    'Basic — KES 500'),
    ('standard', 'Standard — KES 1,000'),
    ('premium',  'Premium — KES 2,000'),
]

TIER_PRICES = {
    'basic':    500,
    'standard': 1000,
    'premium':  2000,
}


class Membership(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending Payment'),
        ('active',    'Active'),
        ('expired',   'Expired'),
        ('suspended', 'Suspended'),
    ]

    writer      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    tier        = models.CharField(max_length=10, choices=TIER_CHOICES, default='basic')
    amount_kes  = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_code  = models.CharField(max_length=20, blank=True)
    checkout_id = models.CharField(max_length=100, blank=True)
    phone       = models.CharField(max_length=15)
    paid_at     = models.DateTimeField(null=True, blank=True)
    expires_at  = models.DateTimeField(null=True, blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.writer.full_name} — {self.tier} — {self.status}"