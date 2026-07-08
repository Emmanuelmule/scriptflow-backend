from django.urls import path
from . import views

urlpatterns = [
    path('summary/',                          views.EarningsSummaryView.as_view(),           name='earnings-summary'),
    path('list/',                             views.EarningsListView.as_view(),              name='earnings-list'),
    path('withdraw/',                         views.WithdrawView.as_view(),                  name='withdraw'),
    path('withdrawal-history/',               views.WithdrawalHistoryView.as_view(),         name='withdrawal-history'),
    path('admin/escrow/',                     views.AdminEscrowListView.as_view(),           name='admin-escrow'),
    path('admin/escrow/<int:pk>/release/',    views.AdminReleaseEscrowView.as_view(),        name='admin-escrow-release'),
    path('admin/withdrawals/',                views.AdminWithdrawalListView.as_view(),       name='admin-withdrawals'),
    path('admin/withdrawals/<int:pk>/process/', views.AdminMarkWithdrawalProcessedView.as_view(), name='admin-withdrawal-process'),
]