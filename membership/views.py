from rest_framework          import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views    import APIView
from django.utils            import timezone
from datetime                import timedelta
from .models      import Membership, TIER_PRICES
from .serializers import MembershipSerializer, STKPushSerializer
from .mpesa       import stk_push


class InitiateMembershipPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = STKPushSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tier   = serializer.validated_data['tier']
        phone  = serializer.validated_data['phone']
        amount = TIER_PRICES[tier]

        # Create pending membership record
        membership = Membership.objects.create(
            writer     = request.user,
            tier       = tier,
            amount_kes = amount,
            phone      = phone,
            status     = 'pending',
        )

        # Format phone: 07XX → 2547XX
        formatted_phone = '254' + phone[1:] if phone.startswith('0') else phone

        # Trigger STK push
        result = stk_push(
            phone       = formatted_phone,
            amount      = amount,
            account_ref = f"WR-{request.user.id:05d}",
            description = f"ScriptFlow {tier.capitalize()} Membership"
        )

        if result.get('ResponseCode') == '0':
            membership.checkout_id = result.get('CheckoutRequestID', '')
            membership.save()
            return Response({
                'message':     'STK Push sent. Enter your M-Pesa PIN on your phone.',
                'checkout_id': membership.checkout_id,
                'membership_id': membership.id,
            })

        membership.delete()
        return Response({'error': 'Failed to initiate payment. Try again.'}, 
                        status=status.HTTP_400_BAD_REQUEST)


class MpesaCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data     = request.data.get('Body', {}).get('stkCallback', {})
        result   = data.get('ResultCode')
        checkout = data.get('CheckoutRequestID')

        try:
            membership = Membership.objects.get(checkout_id=checkout)
        except Membership.DoesNotExist:
            return Response({'status': 'ok'})

        if result == 0:
            # Payment successful
            items = {
                i['Name']: i['Value']
                for i in data.get('CallbackMetadata', {}).get('Item', [])
            }
            membership.mpesa_code = items.get('MpesaReceiptNumber', '')
            membership.paid_at    = timezone.now()
            membership.expires_at = timezone.now() + timedelta(days=30)
            membership.status     = 'active'
            membership.save()

            # Notify writer
            from notification.models import Notification
            Notification.objects.create(
                writer  = membership.writer,
                type    = 'membership',
                message = f"Membership activated! Valid until {membership.expires_at.strftime('%d %b %Y')}."
            )
        else:
            membership.status = 'pending'
            membership.save()

        return Response({'status': 'ok'})


class MembershipStatusView(generics.ListAPIView):
    serializer_class   = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Membership.objects.filter(writer=self.request.user)


class AdminMembershipListView(generics.ListAPIView):
    serializer_class   = MembershipSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset           = Membership.objects.all().order_by('-created_at')