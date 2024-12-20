from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('lists', views.UserListView)
urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('active/<uid64>/<token>/', views.activate, name='active'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('search/<str:account>/', views.AccountSearchView.as_view(), name='search'),
    path('quick/add/now/time/', views.AccountQuickView.as_view(), name='quick'),
    path('quick/list/all/', views.AccountQuickViewList.as_view(), name='quick_list'),
    path('balance/update/', views.BalanceUpdateView.as_view(), name="update_balance"),
    path('balance/withdraw/', views.BalanceWithdrawView.as_view(), name="withdraw_balance"),
    path('balance/transfer/', views.BalanceTransferView.as_view(), name="transfer_balance"),
    path('transactions/', views.TransactionsView.as_view(), name="transactions"),
    path('transactions/<str:type>/', views.TransactionsTypeView.as_view(), name="transactions_type"),
    path('transaction/<int:id>/', views.TransactionDetailsView.as_view(), name="transaction_details"),
    path('transactions/list/all/', views.TransactionsAllView.as_view(), name="transactions_all"),
    path('transaction/read/update/<int:id>/', views.TransactionsReadUpdateView.as_view(), name="transactions_read"),
    path('loans/', views.LoansView.as_view(), name="loan"),
    path('loans/list/all/', views.LoansAllView.as_view(), name="loan_list"),
    path('loan/pay/<int:id>/', views.LoanPayView.as_view(), name="loan_pay"),
    path('pass_change/', views.PasswordChangeView.as_view(), name='pass_change'),
    path('upload/profile/', views.ProfileUploadView.as_view(), name='profile_upload'),
    path('update/profile/', views.ProfileUpdateView.as_view(), name='profile_update'),

    path('deposit/success/', views.DepositSuccess.as_view(), name='deposit_success'),
    path('deposit/failed/', views.DepositFailed.as_view(), name='deposit_failed'),
    path('deposit/cancelled/', views.DepositCancelled.as_view(), name='deposit_cancelled'),
]