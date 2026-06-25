from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',         include('profiles.urls')),
    path('api/work/',         include('work.urls')),
    path('api/membership/',   include('membership.urls')),
    path('api/earning/',      include('earning.urls')),
    path('api/notification/', include('notification.urls')),
]