from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Job, JobApplication, Submission
from .serializers import (
    JobListSerializer, JobDetailSerializer,
    JobCreateSerializer, JobApplicationSerializer, SubmissionSerializer
)
from notification.models import Notification


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class JobBoardView(generics.ListAPIView):
    serializer_class   = JobListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs       = Job.objects.filter(status='open')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs


class ApplyForJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            job = Job.objects.get(pk=pk, status='open')
        except Job.DoesNotExist:
            return Response({'error': 'Job not available.'}, status=404)

        writer = request.user

        # Check if already applied
        if JobApplication.objects.filter(job=job, writer=writer).exists():
            return Response({'error': 'You have already applied for this job.'}, status=400)

        # Check credit balance
        try:
            balance = writer.credit_balance
        except Exception:
            from membership.models import WriterCredits
            balance, _ = WriterCredits.objects.get_or_create(writer=writer)

        if balance.balance < job.credit_cost:
            return Response({
                'error': f'Insufficient credits. This job costs {job.credit_cost} credits. '
                         f'You have {balance.balance} credits.'
            }, status=400)

        # Deduct credits
        balance.spend_credits(job.credit_cost)

        # Create application
        application = JobApplication.objects.create(
            job           = job,
            writer        = writer,
            credits_spent = job.credit_cost,
        )

        # Log credit transaction
        from membership.models import CreditTransaction
        CreditTransaction.objects.create(
            writer      = writer,
            type        = 'spend',
            credits     = job.credit_cost,
            description = f'Applied for job: {job.title}',
        )

        Notification.objects.create(
            writer  = writer,
            type    = 'general',
            message = f'You applied for "{job.title}". {job.credit_cost} credits deducted.'
        )

        return Response({
            'message':         f'Successfully applied for "{job.title}".',
            'credits_spent':   job.credit_cost,
            'credits_remaining': balance.balance,
        })


class MyJobsView(generics.ListAPIView):
    serializer_class   = JobListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(assigned_to=self.request.user).exclude(status='open')


class MyApplicationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        applications = JobApplication.objects.filter(writer=request.user)
        data = [{
            'id':           a.id,
            'job_id':       a.job.id,
            'job_title':    a.job.title,
            'category':     a.job.category,
            'budget_kes':   str(a.job.budget_kes),
            'credit_cost':  a.job.credit_cost,
            'credits_spent':a.credits_spent,
            'status':       a.status,
            'created_at':   a.created_at,
        } for a in applications]
        return Response(data)


class SubmitWorkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            job = Job.objects.get(pk=pk, assigned_to=request.user, status='assigned')
        except Job.DoesNotExist:
            return Response({'error': 'Job not found or not assigned to you.'}, status=404)

        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Content cannot be empty.'}, status=400)

        Submission.objects.create(job=job, writer=request.user, content=content)
        job.status = 'submitted'
        job.save()

        Notification.objects.create(
            writer  = request.user,
            type    = 'submission',
            message = f'Your submission for "{job.title}" is under review.'
        )
        return Response({'message': 'Work submitted successfully.'})


# ── Admin Views ───────────────────────────────────────────────────────────────

class AdminJobCreateView(generics.CreateAPIView):
    serializer_class   = JobCreateSerializer
    permission_classes = [IsAdminUser]


class AdminJobListView(generics.ListAPIView):
    serializer_class   = JobDetailSerializer
    permission_classes = [IsAdminUser]
    queryset           = Job.objects.all()


class AdminJobDetailView(generics.RetrieveUpdateAPIView):
    serializer_class   = JobDetailSerializer
    permission_classes = [IsAdminUser]
    queryset           = Job.objects.all()


class AdminApplicationListView(generics.ListAPIView):
    serializer_class   = JobApplicationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        if job_id:
            return JobApplication.objects.filter(job_id=job_id)
        return JobApplication.objects.filter(status='pending')


class AdminAssignJobView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found.'}, status=404)

        writer_id = request.data.get('writer_id')
        try:
            from profiles.models import Writer
            writer = Writer.objects.get(pk=writer_id)
        except Exception:
            return Response({'error': 'Writer not found.'}, status=404)

        job.assigned_to = writer
        job.status      = 'assigned'
        job.save()

        # Accept this application, reject others
        JobApplication.objects.filter(job=job, writer=writer).update(status='accepted')
        JobApplication.objects.filter(job=job).exclude(writer=writer).update(status='rejected')

        Notification.objects.create(
            writer  = writer,
            type    = 'approval',
            message = f'You have been assigned the job "{job.title}". '
                      f'Budget: KES {job.budget_kes}. Please start writing!'
        )
        return Response({'message': f'Job assigned to {writer.full_name} successfully.'})


class AdminSubmissionListView(generics.ListAPIView):
    serializer_class   = SubmissionSerializer
    permission_classes = [IsAdminUser]
    queryset           = Submission.objects.filter(status='pending')


class AdminReviewSubmissionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            submission = Submission.objects.get(pk=pk)
        except Submission.DoesNotExist:
            return Response({'error': 'Submission not found.'}, status=404)

        action = request.data.get('action')
        notes  = request.data.get('notes', '')

        if action == 'approve':
            submission.status = 'approved'
            submission.save()
            submission.job.status = 'approved'
            submission.job.save()

            from earning.models import Earning
            gross      = float(submission.job.budget_kes)
            commission = gross * 0.15
            net        = gross - commission

            Earning.objects.create(
                writer         = submission.writer,
                job            = submission.job,
                gross_kes      = gross,
                commission_kes = commission,
                net_kes        = net,
                status         = 'available'
            )

            Notification.objects.create(
                writer  = submission.writer,
                type    = 'approval',
                message = f'Your submission for "{submission.job.title}" was approved! '
                          f'KES {net:.2f} added to your balance.'
            )
            return Response({'message': 'Submission approved and earnings credited.'})

        elif action == 'revision':
            submission.status      = 'revision_requested'
            submission.admin_notes = notes
            submission.save()
            submission.job.status  = 'assigned'
            submission.job.save()

            Notification.objects.create(
                writer  = submission.writer,
                type    = 'revision',
                message = f'Revision requested for "{submission.job.title}": {notes}'
            )
            return Response({'message': 'Revision request sent to writer.'})

        return Response({'error': 'Invalid action. Use approve or revision.'}, status=400)