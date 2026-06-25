from rest_framework              import generics, status, permissions
from rest_framework.response     import Response
from rest_framework.views        import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models       import Writer
from .serializers  import (
    RegisterSerializer, LoginSerializer,
    WriterProfileSerializer, AdminWriterListSerializer
)


class RegisterView(generics.CreateAPIView):
    serializer_class  = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        writer = serializer.save()
        refresh = RefreshToken.for_user(writer)
        return Response({
            'message': 'Registration successful. Please complete membership payment.',
            'writer_id': writer.id,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user    = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'role':    user.role,
            'name':    user.full_name,
            'writer_id': user.id,
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = WriterProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminWriterListView(generics.ListAPIView):
    serializer_class   = AdminWriterListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset           = Writer.objects.filter(role='writer').order_by('-created_at')


class AdminWriterDetailView(generics.RetrieveUpdateAPIView):
    serializer_class   = AdminWriterListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset           = Writer.objects.all()