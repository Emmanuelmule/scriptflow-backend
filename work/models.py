from django.db import models
from django.conf import settings

CATEGORY_CHOICES = [
    ('academic',     'Academic Writing'),
    ('seo',          'SEO Writing'),
    ('copywriting',  'Copywriting'),
    ('business',     'Business Reports'),
    ('creative',     'Creative Writing'),
    ('ghostwriting', 'Ghostwriting'),
    ('cv',           'CV Writing'),
    ('blogging',     'Blogging'),
]


def get_credit_cost(budget_kes):
    if budget_kes <= 2000:
        return 1
    elif budget_kes <= 5000:
        return 2
    elif budget_kes <= 10000:
        return 3
    else:
        return 5


class Job(models.Model):
    STATUS_CHOICES = [
        ('open',      'Open'),
        ('assigned',  'Assigned'),
        ('submitted', 'Submitted'),
        ('approved',  'Approved'),
        ('delivered', 'Delivered'),
    ]

    title        = models.CharField(max_length=255)
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    instructions = models.TextField()
    word_count   = models.IntegerField()
    budget_kes   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_cost  = models.IntegerField(default=1)
    deadline     = models.DateTimeField()
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    assigned_to  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_jobs'
    )
    reference_file = models.FileField(upload_to='job_refs/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.credit_cost:
            self.credit_cost = get_credit_cost(float(self.budget_kes))
        super().save(*args, **kwargs)


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    job           = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    writer        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    credits_spent = models.IntegerField()
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['job', 'writer']
        ordering        = ['-created_at']

    def __str__(self):
        return f"{self.writer.full_name} → {self.job.title} ({self.status})"


class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending',            'Pending Review'),
        ('approved',           'Approved'),
        ('revision_requested', 'Revision Requested'),
    ]

    job          = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='submissions')
    writer       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    content      = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    admin_notes  = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission: {self.job.title} by {self.writer.full_name}"