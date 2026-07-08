from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Job, Submission
from .serializers import (
    JobListSerializer, JobDetailSerializer,
    JobCreateSerializer, SubmissionSerializer
)
from notification.models import Notification


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class JobBoardView(generics.ListAPIView):
    serializer_class = JobListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Job.objects.filter(status='open')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs


class ClaimJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            job = Job.objects.get(pk=pk, status='open')
        except Job.DoesNotExist:
            return Response({'error': 'Job not available.'}, status=404)
        job.claimed_by = request.user
        job.status = 'claimed'
        job.save()
        return Response({'message': f'Job "{job.title}" claimed successfully.'})


class MyJobsView(generics.ListAPIView):
    serializer_class = JobListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(
            claimed_by=self.request.user
        ).exclude(status='open')


class SubmitWorkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            job = Job.objects.get(pk=pk, claimed_by=request.user, status='claimed')
        except Job.DoesNotExist:
            return Response({'error': 'Job not found or not yours.'}, status=404)
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Content cannot be empty.'}, status=400)
        Submission.objects.create(job=job, writer=request.user, content=content)
        job.status = 'submitted'
        job.save()
        Notification.objects.create(
            writer=request.user,
            type='submission',
            message=f'Your submission for "{job.title}" is under review.'
        )
        return Response({'message': 'Work submitted successfully.'})


class AdminJobCreateView(generics.CreateAPIView):
    serializer_class = JobCreateSerializer
    permission_classes = [IsAdminUser]


class AdminJobListView(generics.ListAPIView):
    serializer_class = JobDetailSerializer
    permission_classes = [IsAdminUser]
    queryset = Job.objects.all()


class AdminJobDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = JobDetailSerializer
    permission_classes = [IsAdminUser]
    queryset = Job.objects.all()


class AdminSubmissionListView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAdminUser]
    queryset = Submission.objects.filter(status='pending')


class AdminReviewSubmissionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            submission = Submission.objects.get(pk=pk)
        except Submission.DoesNotExist:
            return Response({'error': 'Submission not found.'}, status=404)

        action = request.data.get('action')
        notes = request.data.get('notes', '')

        if action == 'approve':
            submission.status = 'approved'
            submission.save()
            submission.job.status = 'approved'
            submission.job.save()

            from earning.models import Earning
            Earning.objects.create(
                writer=submission.writer,
                job=submission.job,
                amount_usd=submission.job.pay_usd,
                status='available'
            )
            Notification.objects.create(
                writer=submission.writer,
                type='approval',
                message=f'Your submission for "{submission.job.title}" was approved!'
            )
            return Response({'message': 'Submission approved and earnings credited.'})

        elif action == 'revision':
            submission.status = 'revision_requested'
            submission.admin_notes = notes
            submission.save()
            submission.job.status = 'claimed'
            submission.job.save()
            Notification.objects.create(
                writer=submission.writer,
                type='revision',
                message=f'Revision requested for "{submission.job.title}": {notes}'
            )
            return Response({'message': 'Revision request sent to writer.'})

        return Response({'error': 'Invalid action. Use approve or revision.'}, status=400)