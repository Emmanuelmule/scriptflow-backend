from django.contrib import admin
from .models import Job, JobApplication, Submission


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'budget_kes', 'credit_cost', 'status', 'deadline']
    list_filter  = ['status', 'category']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'writer', 'credits_spent', 'status', 'created_at']
    list_filter  = ['status']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['job', 'writer', 'status', 'submitted_at']
    list_filter  = ['status']