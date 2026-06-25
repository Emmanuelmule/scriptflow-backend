from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/',               views.RegisterView.as_view(),             name='register'),
    path('login/',                  views.LoginView.as_view(),                name='login'),
    path('token/refresh/',          TokenRefreshView.as_view(),               name='token_refresh'),
    path('profile/',                views.ProfileView.as_view(),              name='profile'),
    path('admin/writers/',          views.AdminWriterListView.as_view(),      name='admin-writers'),
    path('admin/writers/<int:pk>/', views.AdminWriterDetailView.as_view(),    name='admin-writer-detail'),
]