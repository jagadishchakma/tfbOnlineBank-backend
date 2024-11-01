from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from . import serializers
from .models import Profile, Transaction, QuickTransfer, Loan
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import IsAuthenticated
from tfbOnlineBanking.utils import frontend_link
from libs.payment_request import payment_request

#user list
class UserListView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserListSerializer


#user registration
class RegisterView(APIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()
            return Response('Registration successful! please verify your email for activate  account',
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#user email verification
def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token) and user.is_active == False:
        user.is_active = True
        user.save()
        # save history
        Transaction.objects.create(
            user=user,
            amount=0,
            type='Registration',
            message='Registration successful',
        )
        return HttpResponseRedirect(f'{frontend_link}/login?status=success')
    elif user is not None and default_token_generator.check_token(user, token) and user.is_active == True:
        return HttpResponseRedirect(f'{frontend_link}/account/login?status=already_verified')
    return HttpResponseRedirect(f'{frontend_link}/account/login?status=failure')


#user login
class LoginView(APIView):
    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            account_no = serializer.validated_data['account_no']
            password = serializer.validated_data['password']

            # Find the User associated with the provided account_no
            try:
                profile = Profile.objects.get(account_no=account_no)
                user = profile.user
            except Profile.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=400)

            # Authenticate the user using the username
            user = authenticate(username=user.username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({'token': token.key, 'user_id': user.id})
            else:
                return Response({'error': 'Invalid credentials'}, status=400)

        return Response(serializer.errors, status=400)


#user logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print(request.user)
            request.user.auth_token.delete()
            return Response({'success': 'logout'})
        except Exception as e:
            return Response({'error': 'logout failed'})


#user balance update
class BalanceUpdateView(UpdateAPIView):
    serializer_class = serializers.BalanceUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        profile = self.request.user.profile
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        balance = serializer.validated_data['balance']
        account_no = serializer.validated_data['account_no']
        if account_no != profile.account_no:
            return Response({'error': 'Account not match'}, status=400)
        
        url = payment_request(balance,self.request.user)
        return Response({'payment_url': url}, status=status.HTTP_200_OK)


#payment deposit success
class  DepositSuccess(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('value_a')
        balance = int(float(request.data.get('amount')))
        tran_id = request.data.get('tran_id')
        user = User.objects.get(id=user_id)
        profile = user.profile
        profile.balance += balance
        profile.deposit += balance
        profile.save(
            update_fields=['balance','deposit']
        )
        #save history
        Transaction.objects.create(
            user=user,
            amount=balance,
            type='Deposited',
            tran_id=tran_id,
            message=f'Deposited successfully amount of ${balance}',
        )
        return HttpResponseRedirect(f'{frontend_link}/deposit?status=success')


#payment deposit failed
class DepositFailed(APIView):
    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(f'{frontend_link}/deposit?status=failed')

#payment deposit failed
class DepositCancelled(APIView):
    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(f'{frontend_link}/deposit?status=cancelled')




#user balance withdraw
class BalanceWithdrawView(UpdateAPIView):
    serializer_class = serializers.BalanceWithdrawSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        profile = self.request.user.profile
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        balance = serializer.validated_data['balance']
        account_no = serializer.validated_data['account_no']
        if account_no != profile.account_no:
            return Response({'error': 'Account not match'}, status=400)
        profile.balance -= balance
        profile.withdraw += balance
        profile.save(
            update_fields=['balance', 'withdraw']
        )

        # save history
        Transaction.objects.create(
            user=self.request.user,
            amount=balance,
            type='Withdraw',
            message=f'Withdraw successfully amount of ${balance}'
        )

        return Response({'balance': profile.balance}, status=status.HTTP_200_OK)


#user balance transfer
class BalanceTransferView(UpdateAPIView):
    serializer_class = serializers.BalanceTransferSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        sender_profile = self.request.user.profile
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        balance = serializer.validated_data['balance']
        sender_account_no = serializer.validated_data['sender_account_no']
        receiver_account_no = serializer.validated_data['receiver_account_no']

        #check sender profile
        if sender_account_no != sender_profile.account_no:
            return Response({'error': 'Sender account not match'}, status=400)
        #check receiver profile
        try:
            receiver_profile = Profile.objects.get(account_no=receiver_account_no)
        except Profile.DoesNotExist:
            return Response({'error': 'Receiver account not match'}, status=400)

        #update sender profile
        sender_profile.balance -= balance
        sender_profile.transfer += balance
        sender_profile.save(
            update_fields=['balance', 'transfer']
        )

        # update receiver profile
        receiver_profile.balance += balance
        receiver_profile.save(
            update_fields=['balance']
        )

        # save history
        Transaction.objects.create(
            #sender transaction history
            user=self.request.user,
            amount=balance,
            type='Transfer',
            message=f'Transfer successfully from {sender_profile.account_no} to {receiver_profile.account_no} amount of ${balance}',
        )
        # save history
        Transaction.objects.create(
            # sender transaction history
            user=User.objects.get(profile__account_no=receiver_account_no),
            amount=balance,
            type='Transfer',
            message=f'Transfer receive successfully from {sender_profile.account_no} amount of ${balance}',
        )

        return Response({'balance': balance}, status=status.HTTP_200_OK)


#password change view
class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'Password changed successfully!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#image profile upload
class ProfileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = serializers.ProfileImageSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile image updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#profile personal info update
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        user_serializer = serializers.UserSerializer(user, data=request.data, partial=True)
        profile = request.user.profile
        profile_serializer = serializers.ProfileSerializer(profile, data=request.data, partial=True)
        if user_serializer.is_valid() and profile_serializer.is_valid():
            user_serializer.save()
            profile_serializer.save()
            return Response({'message': 'Profile personal information updated successfully'}, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#transaction type
class TransactionsView(ListAPIView):
    serializer_class = serializers.TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user, read=False).order_by('-id')


#transaction type
class TransactionsTypeView(ListAPIView):
    serializer_class = serializers.TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        transaction_type = self.kwargs.get('type')
        return Transaction.objects.filter(user=user, type=transaction_type).order_by('-id')


#transaction all
class TransactionsAllView(ListAPIView):
    serializer_class = serializers.TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(user=user).order_by('-id')

#loan all
class LoansAllView(ListAPIView):
    serializer_class = serializers.LoansSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Loan.objects.filter(user=user, status=True).order_by('-id')




#loan requested
class LoansView(APIView):
    serializer_class = serializers.LoansSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            # email verification setup
            user = self.request.user
            user = self.request.user
            mail_subject = "Loan Request"
            message = f"Your Loan request successfully send amount of ${request.data['amount']}.Pleas wait until admin approve your request."
            mail_body = render_to_string('loan_confirm.html', {'message': message})
            send_mail = EmailMultiAlternatives(mail_subject, '', to=[user.email])
            send_mail.attach_alternative(mail_body, 'text/html')
            send_mail.send()

            # save history
            amount = request.data['amount']
            message = f'Your Loan request successfully send amount of {amount}.Pleas wait until admin approve your request.'
            Transaction.objects.create(
                user=self.request.user,
                amount=amount,
                type='Loan',
                message=message
            )

            return Response('Loan request apply successfully.Wait until admin approve your request',
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoanPayView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, *args, **kwargs):
        loan_id = kwargs.get('id')
        loan = Loan.objects.get(id=loan_id)
        loan.pay = True
        loan.save(
            update_fields=['pay']
        )
        user_profile = self.request.user.profile
        user_profile.balance -= loan.amount
        user_profile.save(
            update_fields = ['balance']
        )
        return Response({'success':'Loan pay successfully'})

#account search view
class AccountSearchView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        account_number = self.kwargs['account']  # Get the account number from the URL
        # Adjust this filter logic according to your model's fields
        return get_object_or_404(Profile, account_no=account_number)


#quick transfer view
class AccountQuickView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.QuickTransferSerializer

    def post(self, request, *args, **kwargs):
        receiver_account = request.data['account']
        receiver = Profile.objects.get(account_no=receiver_account)
        data = request.data.copy()
        data['sender'] = request.user.id
        data['receiver'] = receiver.user.id
        serializer = self.serializer_class(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Quick transfer added successful!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountQuickViewList(ListAPIView):
    serializer_class = serializers.QuickTransferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return QuickTransfer.objects.filter(sender=user).order_by('-id')


class TransactionsReadUpdateView(APIView):
    serializer_class = serializers.TransactionSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        user = self.request.user

        try:
            transaction = Transaction.objects.get(user=user, read=False, id=id)
        except Transaction.DoesNotExist:
            return Response({'message': 'Transaction updated successfully'}, status=status.HTTP_200_OK)

        transaction.read = True
        transaction.save(
            update_fields=['read']
        )
        return Response({'message': 'Transaction updated successfully'}, status=status.HTTP_200_OK)


#transaction details view
class TransactionDetailsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer

    def get_object(self):
        id = self.kwargs['id']
        return get_object_or_404(Transaction, id=id, user=self.request.user)
