from django.urls import path
from . import views

urlpatterns = [
    path('summary/',                        views.EarningsSummaryView.as_view(),         name='earnings-summary'),
    path('list/',                           views.EarningsListView.as_view(),            name='earnings-list'),
    path('withdraw/',                       views.WithdrawView.as_view(),                name='withdraw'),
    path('payout-history/',                 views.PayoutHistoryView.as_view(),           name='payout-history'),
    path('admin/payouts/',                  views.AdminPayoutListView.as_view(),         name='admin-payouts'),
    path('admin/payouts/<int:pk>/process/', views.AdminMarkPayoutProcessedView.as_view(),name='admin-payout-process'),
]