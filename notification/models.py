from django.db import models
from django.conf import settings

TYPE_CHOICES = [
    ('membership', 'Membership'),
    ('submission', 'Submission'),
    ('approval',   'Approval'),
    ('revision',   'Revision'),
    ('payout',     'Payout'),
    ('general',    'General'),
]


class Notification(models.Model):
    writer    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type      = models.CharField(max_length=15, choices=TYPE_CHOICES, default='general')
    message   = models.TextField()
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.writer.full_name} — {self.type}"