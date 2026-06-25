from django.urls import path
from . import views

urlpatterns = [
    path('initiate/',        views.InitiateMembershipPaymentView.as_view(), name='membership-initiate'),
    path('mpesa-callback/',  views.MpesaCallbackView.as_view(),             name='mpesa-callback'),
    path('my-membership/',   views.MembershipStatusView.as_view(),          name='my-membership'),
    path('admin/all/',       views.AdminMembershipListView.as_view(),       name='admin-memberships'),
]