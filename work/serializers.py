from rest_framework import serializers
from .models import Job, JobApplication, Submission


class JobListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)

    class Meta:
        model  = Job
        fields = [
            'id', 'title', 'category', 'word_count', 'budget_kes',
            'credit_cost', 'deadline', 'status', 'assigned_to_name', 'created_at'
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)

    class Meta:
        model  = Job
        fields = '__all__'


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Job
        fields = [
            'title', 'category', 'instructions', 'word_count',
            'budget_kes', 'credit_cost', 'deadline', 'reference_file'
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(source='writer.full_name', read_only=True)
    job_title   = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model  = JobApplication
        fields = [
            'id', 'job', 'job_title', 'writer', 'writer_name',
            'credits_spent', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'writer', 'credits_spent', 'status', 'created_at']


class SubmissionSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(source='writer.full_name', read_only=True)
    job_title   = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model  = Submission
        fields = [
            'id', 'job', 'job_title', 'writer', 'writer_name',
            'content', 'submitted_at', 'status', 'admin_notes'
        ]
        read_only_fields = ['id', 'writer', 'submitted_at', 'status', 'admin_notes']