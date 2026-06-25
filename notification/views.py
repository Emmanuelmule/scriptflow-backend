from rest_framework          import generics, permissions
from rest_framework.response import Response
from rest_framework.views    import APIView
from .models      import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(writer=self.request.user)


class MarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(
            writer=request.user, is_read=False
        ).update(is_read=True)
        return Response({'message': 'All notifications marked as read.'})


class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            writer=request.user, is_read=False
        ).count()
        return Response({'unread_count': count})