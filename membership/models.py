from django.db import models
from django.conf import settings


class CreditPackage(models.Model):
    name       = models.CharField(max_length=100)
    credits    = models.IntegerField()
    price_kes  = models.DecimalField(max_digits=10, decimal_places=2)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.credits} credits — KES {self.price_kes}"


class CreditTransaction(models.Model):
    TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('spend',    'Spend'),
        ('refund',   'Refund'),
    ]
    writer     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_transactions'
    )
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    credits     = models.IntegerField()
    description = models.CharField(max_length=255, blank=True)
    mpesa_code  = models.CharField(max_length=20, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.writer.full_name} — {self.type} — {self.credits} credits"


class WriterCredits(models.Model):
    writer  = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_balance'
    )
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.writer.full_name} — {self.balance} credits"

    def add_credits(self, amount):
        self.balance += amount
        self.save()

    def spend_credits(self, amount):
        if self.balance < amount:
            raise ValueError("Insufficient credits")
        self.balance -= amount
        self.save()