from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone
from .models import Earning, Payout
from notification.models import Notification

MINIMUM_WITHDRAWAL_KES = 7500


class EarningsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        writer   = request.user
        earnings = writer.earnings.all()

        total     = earnings.aggregate(t=Sum('net_kes'))['t'] or 0
        available = earnings.filter(status='available').aggregate(t=Sum('net_kes'))['t'] or 0
        pending   = earnings.filter(status='pending').aggregate(t=Sum('net_kes'))['t'] or 0
        paid      = earnings.filter(status='paid').aggregate(t=Sum('net_kes'))['t'] or 0

        return Response({
            'total_earned':       float(total),
            'available':          float(available),
            'pending':            float(pending),
            'paid_out':           float(paid),
            'minimum_withdrawal': MINIMUM_WITHDRAWAL_KES,
            'can_withdraw':       float(available) >= MINIMUM_WITHDRAWAL_KES,
            'threshold_progress': min(float(available) / MINIMUM_WITHDRAWAL_KES * 100, 100),
            'currency':           'KES',
        })


class EarningsListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        earnings = request.user.earnings.all()
        data = [{
            'id':             e.id,
            'job_title':      e.job.title,
            'gross_kes':      str(e.gross_kes),
            'commission_kes': str(e.commission_kes),
            'net_kes':        str(e.net_kes),
            'status':         e.status,
            'created_at':     e.created_at,
        } for e in earnings]
        return Response(data)


class WithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        writer    = request.user
        available = writer.earnings.filter(status='available').aggregate(
            t=Sum('net_kes')
        )['t'] or 0

        if float(available) < MINIMUM_WITHDRAWAL_KES:
            return Response({
                'error': f'Minimum withdrawal is KES {MINIMUM_WITHDRAWAL_KES}. '
                         f'You have KES {available:.2f} available.'
            }, status=status.HTTP_400_BAD_REQUEST)

        mpesa_number = request.data.get('mpesa_number', '')
        if not mpesa_number:
            return Response({'error': 'M-Pesa number is required.'}, status=400)

        payout = Payout.objects.create(
            writer       = writer,
            amount_kes   = available,
            mpesa_number = mpesa_number,
            status       = 'pending',
        )

        writer.earnings.filter(status='available').update(status='paid')

        Notification.objects.create(
            writer  = writer,
            type    = 'payout',
            message = f'Withdrawal request of KES {available:.2f} received. '
                      f'Processing within 1-3 business days.'
        )

        return Response({
            'message':    f'Withdrawal of KES {available:.2f} submitted successfully.',
            'payout_id':  payout.id,
            'amount_kes': float(available),
        })


class PayoutHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        payouts = request.user.payouts.all()
        data = [{
            'id':           p.id,
            'amount_kes':   str(p.amount_kes),
            'mpesa_number': p.mpesa_number,
            'mpesa_code':   p.mpesa_code,
            'status':       p.status,
            'created_at':   p.created_at,
        } for p in payouts]
        return Response(data)


class AdminPayoutListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        payouts = Payout.objects.filter(status='pending')
        data = [{
            'id':           p.id,
            'writer':       p.writer.full_name,
            'amount_kes':   str(p.amount_kes),
            'mpesa_number': p.mpesa_number,
            'status':       p.status,
            'created_at':   p.created_at,
        } for p in payouts]
        return Response(data)


class AdminMarkPayoutProcessedView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            payout = Payout.objects.get(pk=pk)
        except Payout.DoesNotExist:
            return Response({'error': 'Payout not found.'}, status=404)

        payout.status       = 'processed'
        payout.processed_at = timezone.now()
        payout.mpesa_code   = request.data.get('mpesa_code', '')
        payout.save()

        Notification.objects.create(
            writer  = payout.writer,
            type    = 'payout',
            message = f'Your payout of KES {payout.amount_kes} has been processed via M-Pesa.'
        )
        return Response({'message': 'Payout marked as processed.'})