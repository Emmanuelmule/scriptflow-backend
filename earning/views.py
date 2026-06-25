from rest_framework          import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views    import APIView
from django.db.models        import Sum
from django.utils            import timezone
from .models      import Earning, Payout
from .serializers import EarningSerializer, PayoutSerializer, WithdrawRequestSerializer
from notification.models import Notification

MINIMUM_WITHDRAWAL = 10.00


class EarningsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        writer   = request.user
        earnings = writer.earnings.all()

        total     = earnings.aggregate(t=Sum('amount_usd'))['t'] or 0
        available = earnings.filter(status='available').aggregate(t=Sum('amount_usd'))['t'] or 0
        pending   = earnings.filter(status='pending').aggregate(t=Sum('amount_usd'))['t'] or 0
        paid      = earnings.filter(status='paid').aggregate(t=Sum('amount_usd'))['t'] or 0

        return Response({
            'total_earned':        float(total),
            'available':           float(available),
            'pending':             float(pending),
            'paid_out':            float(paid),
            'minimum_withdrawal':  MINIMUM_WITHDRAWAL,
            'can_withdraw':        float(available) >= MINIMUM_WITHDRAWAL,
            'threshold_progress':  min(float(available) / MINIMUM_WITHDRAWAL * 100, 100),
        })


class EarningsListView(generics.ListAPIView):
    serializer_class   = EarningSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Earning.objects.filter(writer=self.request.user)


class WithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = WithdrawRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        writer    = request.user
        available = writer.earnings.filter(status='available').aggregate(
            t=Sum('amount_usd')
        )['t'] or 0

        if float(available) < MINIMUM_WITHDRAWAL:
            return Response({
                'error': f'Minimum withdrawal is ${MINIMUM_WITHDRAWAL}. '
                         f'You have ${available:.2f} available.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Deduct processing fee
        fee    = 0.50
        amount = float(available) - fee

        payout = Payout.objects.create(
            writer     = writer,
            amount_usd = amount,
            method     = serializer.validated_data['method'],
            reference  = serializer.validated_data['account'],
            status     = 'pending',
        )

        # Mark earnings as paid
        writer.earnings.filter(status='available').update(status='paid')

        Notification.objects.create(
            writer  = writer,
            type    = 'payout',
            message = f'Withdrawal request of ${amount:.2f} received. '
                      f'Processing on the next payout date.'
        )

        return Response({
            'message':    f'Withdrawal request submitted. ${amount:.2f} will be sent via '
                          f'{payout.get_method_display()}.',
            'payout_id':  payout.id,
            'amount_usd': amount,
        })


class PayoutHistoryView(generics.ListAPIView):
    serializer_class   = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payout.objects.filter(writer=self.request.user)


class AdminPayoutListView(generics.ListAPIView):
    serializer_class   = PayoutSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset           = Payout.objects.filter(status='pending')


class AdminMarkPayoutProcessedView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            payout = Payout.objects.get(pk=pk)
        except Payout.DoesNotExist:
            return Response({'error': 'Payout not found.'}, status=404)

        payout.status       = 'processed'
        payout.processed_at = timezone.now()
        payout.reference    = request.data.get('reference', payout.reference)
        payout.amount_kes   = request.data.get('amount_kes')
        payout.exchange_rate = request.data.get('exchange_rate')
        payout.save()

        Notification.objects.create(
            writer  = payout.writer,
            type    = 'payout',
            message = f'Your payout of ${payout.amount_usd} has been processed via '
                      f'{payout.get_method_display()}.'
        )
        return Response({'message': 'Payout marked as processed.'})