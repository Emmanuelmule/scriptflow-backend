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

VISIBILITY_CHOICES = [
    ('all',      'All Tiers'),
    ('standard', 'Standard & Premium'),
    ('premium',  'Premium Only'),
]


class Job(models.Model):
    STATUS_CHOICES = [
        ('open',      'Open'),
        ('claimed',   'Claimed'),
        ('submitted', 'Submitted'),
        ('approved',  'Approved'),
        ('delivered', 'Delivered'),
    ]

    title        = models.CharField(max_length=255)
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    instructions = models.TextField()
    word_count   = models.IntegerField()
    pay_usd      = models.DecimalField(max_digits=8, decimal_places=2)
    deadline     = models.DateTimeField()
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    claimed_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='claimed_jobs'
    )
    visibility   = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='all')
    reference_file = models.FileField(upload_to='job_refs/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


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