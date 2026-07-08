from django.urls import path
from . import views

urlpatterns = [
    path('packages/',          views.CreditPackageListView.as_view(),    name='credit-packages'),
    path('balance/',           views.CreditBalanceView.as_view(),        name='credit-balance'),
    path('transactions/',      views.CreditTransactionListView.as_view(),name='credit-transactions'),
    path('purchase/',          views.InitiateCreditPurchaseView.as_view(),name='credit-purchase'),
    path('admin/packages/',    views.AdminCreditPackageView.as_view(),   name='admin-packages'),
]