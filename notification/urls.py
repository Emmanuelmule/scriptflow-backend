from django.urls import path
from . import views

urlpatterns = [
    path('',           views.NotificationListView.as_view(), name='notifications'),
    path('mark-read/', views.MarkAllReadView.as_view(),      name='mark-read'),
    path('unread/',    views.UnreadCountView.as_view(),      name='unread-count'),
]