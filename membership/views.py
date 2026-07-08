from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CreditPackage, CreditTransaction, WriterCredits


class CreditPackageListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        packages = CreditPackage.objects.filter(is_active=True)
        data = [{
            'id':        p.id,
            'name':      p.name,
            'credits':   p.credits,
            'price_kes': str(p.price_kes),
        } for p in packages]
        return Response(data)


class CreditBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        balance, _ = WriterCredits.objects.get_or_create(writer=request.user)
        return Response({'balance': balance.balance})


class CreditTransactionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        txns = CreditTransaction.objects.filter(
            writer=request.user
        ).order_by('-created_at')[:20]
        data = [{
            'id':          t.id,
            'type':        t.type,
            'credits':     t.credits,
            'description': t.description,
            'created_at':  t.created_at,
        } for t in txns]
        return Response(data)


class InitiateCreditPurchaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        package_id = request.data.get('package_id')
        phone      = request.data.get('phone')

        try:
            package = CreditPackage.objects.get(id=package_id, is_active=True)
        except CreditPackage.DoesNotExist:
            return Response({'error': 'Invalid package.'}, status=400)

        # TODO: Trigger M-Pesa STK Push here
        # For now simulate success
        balance, _ = WriterCredits.objects.get_or_create(writer=request.user)
        balance.add_credits(package.credits)

        CreditTransaction.objects.create(
            writer      = request.user,
            type        = 'purchase',
            credits     = package.credits,
            description = f'Purchased {package.name} package',
        )

        return Response({
            'message':     f'Successfully purchased {package.credits} credits.',
            'new_balance': balance.balance,
        })


class AdminCreditPackageView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = CreditPackage.objects.all()

    def get(self, request):
        packages = CreditPackage.objects.all()
        data = [{
            'id':        p.id,
            'name':      p.name,
            'credits':   p.credits,
            'price_kes': str(p.price_kes),
            'is_active': p.is_active,
        } for p in packages]
        return Response(data)

    def post(self, request):
        name      = request.data.get('name')
        credits   = request.data.get('credits')
        price_kes = request.data.get('price_kes')
        package   = CreditPackage.objects.create(
            name=name, credits=credits, price_kes=price_kes
        )
        return Response({
            'id':        package.id,
            'name':      package.name,
            'credits':   package.credits,
            'price_kes': str(package.price_kes),
        }, status=201)