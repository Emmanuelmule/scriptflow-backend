from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

SPECIALTY_CHOICES = [
    ('academic',    'Academic Writing'),
    ('seo',         'SEO Writing'),
    ('copywriting', 'Copywriting'),
    ('business',    'Business Reports'),
    ('creative',    'Creative Writing'),
    ('ghostwriting','Ghostwriting'),
    ('cv',          'CV Writing'),
    ('blogging',    'Blogging'),
]

EXPERIENCE_CHOICES = [
    ('0-1', '0–1 years'),
    ('1-3', '1–3 years'),
    ('3-5', '3–5 years'),
    ('5+',  '5+ years'),
]

EDUCATION_CHOICES = [
    ('high_school', 'High School'),
    ('diploma',     'Diploma'),
    ('bachelors',   'Bachelor\'s Degree'),
    ('masters',     'Master\'s Degree'),
    ('phd',         'PhD'),
]


class WriterManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',     True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role',         'admin')
        return self.create_user(email, password, **extra_fields)


class Writer(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [('writer', 'Writer'), ('admin', 'Admin')]

    email       = models.EmailField(unique=True)
    full_name   = models.CharField(max_length=255)
    phone       = models.CharField(max_length=15)
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES, default='writer')
    bio         = models.TextField(blank=True)
    specialties = models.JSONField(default=list)
    experience  = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, default='0-1')
    education   = models.CharField(max_length=20, choices=EDUCATION_CHOICES, default='bachelors')
    rating      = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    photo       = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    groups      = models.ManyToManyField(
        'auth.Group',
        related_name='writer_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',)
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='writer_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
          )

    objects = WriterManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def is_membership_active(self):
        return self.memberships.filter(status='active').exists()