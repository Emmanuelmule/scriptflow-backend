from rest_framework          import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views    import APIView
from django.db.models        import Sum
from django.utils            import timezone
from .models import WriterEarning, EscrowAccount, Withdrawal

MINIMUM_WITHDRAWAL_KES = 2500


class EarningsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        writer   = request.user
        earnings = writer.writer_earnings.all()

        total     = earnings.aggregate(t=Sum('net_amount_kes'))['t'] or 0
        available = earnings.filter(status='available').aggregate(t=Sum('net_amount_kes'))['t'] or 0
        pending   = earnings.filter(status='pending').aggregate(t=Sum('net_amount_kes'))['t'] or 0
        withdrawn = earnings.filter(status='withdrawn').aggregate(t=Sum('net_amount_kes'))['t'] or 0

        return Response({
            'total_earned_kes':      float(total),
            'available_kes':         float(available),
            'pending_kes':           float(pending),
            'withdrawn_kes':         float(withdrawn),
            'minimum_withdrawal':    MINIMUM_WITHDRAWAL_KES,
            'can_withdraw':          float(available) >= MINIMUM_WITHDRAWAL_KES,
            'threshold_progress':    min(float(available) / MINIMUM_WITHDRAWAL_KES * 100, 100),
        })


class EarningsListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WriterEarning.objects.filter(writer=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = [{
            'id':               e.id,
            'job_title':        e.job.title,
            'gross_amount_kes': float(e.gross_amount_kes),
            'commission_kes':   float(e.commission_kes),
            'net_amount_kes':   float(e.net_amount_kes),
            'status':           e.status,
            'created_at':       e.created_at,
        } for e in qs]
        return Response({'count': len(data), 'results': data})


class WithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        writer    = request.user
        available = writer.writer_earnings.filter(
            status='available'
        ).aggregate(t=Sum('net_amount_kes'))['t'] or 0

        if float(available) < MINIMUM_WITHDRAWAL_KES:
            return Response({
                'error': f'Minimum withdrawal is KES {MINIMUM_WITHDRAWAL_KES}. '
                         f'You have KES {available:.2f} available.'
            }, status=status.HTTP_400_BAD_REQUEST)

        mpesa_number = request.data.get('mpesa_number')
        if not mpesa_number:
            return Response({'error': 'M-Pesa number is required.'}, status=400)

        withdrawal = Withdrawal.objects.create(
            writer       = writer,
            amount_kes   = available,
            mpesa_number = mpesa_number,
            status       = 'pending',
        )

        writer.writer_earnings.filter(status='available').update(status='withdrawn')

        from notification.models import Notification
        Notification.objects.create(
            writer  = writer,
            type    = 'payout',
            message = f'Withdrawal request of KES {available:.2f} received. Processing within 24 hours.'
        )

        return Response({
            'message':    f'Withdrawal of KES {available:.2f} submitted successfully.',
            'withdrawal_id': withdrawal.id,
            'amount_kes': float(available),
        })


class WithdrawalHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Withdrawal.objects.filter(writer=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = [{
            'id':           w.id,
            'amount_kes':   float(w.amount_kes),
            'mpesa_number': w.mpesa_number,
            'mpesa_code':   w.mpesa_code,
            'status':       w.status,
            'created_at':   w.created_at,
        } for w in qs]
        return Response({'count': len(data), 'results': data})


class AdminEscrowListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        escrows = EscrowAccount.objects.all().order_by('-created_at')
        data = [{
            'id':                  e.id,
            'job_title':           e.job.title,
            'client_payment_kes':  float(e.client_payment_kes),
            'commission_kes':      float(e.commission_kes),
            'writer_amount_kes':   float(e.writer_amount_kes),
            'status':              e.status,
            'auto_release_date':   e.auto_release_date,
            'created_at':          e.created_at,
        } for e in escrows]
        return Response({'count': len(data), 'results': data})


class AdminReleaseEscrowView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            escrow = EscrowAccount.objects.get(pk=pk)
        except EscrowAccount.DoesNotExist:
            return Response({'error': 'Escrow not found.'}, status=404)

        escrow.status      = 'released'
        escrow.released_at = timezone.now()
        escrow.save()

        WriterEarning.objects.filter(job=escrow.job).update(status='available')

        from notification.models import Notification
        Notification.objects.create(
            writer  = escrow.job.assigned_to,
            type    = 'payout',
            message = f'Payment of KES {escrow.writer_amount_kes} for "{escrow.job.title}" has been released.'
        )

        return Response({'message': 'Escrow released successfully.'})


class AdminWithdrawalListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        withdrawals = Withdrawal.objects.filter(status='pending').order_by('-created_at')
        data = [{
            'id':           w.id,
            'writer_name':  w.writer.full_name,
            'amount_kes':   float(w.amount_kes),
            'mpesa_number': w.mpesa_number,
            'status':       w.status,
            'created_at':   w.created_at,
        } for w in withdrawals]
        return Response({'count': len(data), 'results': data})


class AdminMarkWithdrawalProcessedView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            withdrawal = Withdrawal.objects.get(pk=pk)
        except Withdrawal.DoesNotExist:
            return Response({'error': 'Withdrawal not found.'}, status=404)

        withdrawal.status       = 'processed'
        withdrawal.mpesa_code   = request.data.get('mpesa_code', '')
        withdrawal.processed_at = timezone.now()
        withdrawal.save()

        from notification.models import Notification
        Notification.objects.create(
            writer  = withdrawal.writer,
            type    = 'payout',
            message = f'Your withdrawal of KES {withdrawal.amount_kes} has been processed via M-Pesa.'
        )
        return Response({'message': 'Withdrawal marked as processed.'})