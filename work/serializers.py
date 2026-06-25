from rest_framework import serializers
from .models import Job, Submission


class JobListSerializer(serializers.ModelSerializer):
    claimed_by_name = serializers.CharField(source='claimed_by.full_name', read_only=True)

    class Meta:
        model  = Job
        fields = [
            'id', 'title', 'category', 'word_count', 'pay_usd',
            'deadline', 'status', 'visibility', 'claimed_by_name', 'created_at'
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Job
        fields = '__all__'


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Job
        fields = [
            'title', 'category', 'instructions', 'word_count',
            'pay_usd', 'deadline', 'visibility', 'reference_file'
        ]


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