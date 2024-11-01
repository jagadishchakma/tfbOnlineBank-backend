from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile, Transaction, Loan, QuickTransfer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from tfbOnlineBanking.utils import backend_link
import random


# user serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


#user profile serializer
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'profile']


#user lists serializer
class UserListSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = '__all__'


#user registration serializer
def generate_unique_account_number():
    while True:
        account_no = str(random.randint(100000000000, 999999999999))
        if not Profile.objects.filter(account_no=account_no).exists():
            return account_no


class RegistrationSerializer(serializers.ModelSerializer):
    street_address = serializers.CharField(required=True)
    phone_no = serializers.IntegerField(required=True)
    account_type = serializers.CharField(required=True)
    birth_year = serializers.IntegerField(required=True)
    birth_month = serializers.IntegerField(required=True)
    birth_date = serializers.IntegerField(required=True)
    gender = serializers.CharField(required=True)
    zip_code = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password', 'street_address',
                  'phone_no', 'account_type', 'birth_year', 'birth_month', 'birth_date', 'gender', 'zip_code', 'city',
                  'state', 'country']

    def save(self):
        #retrive user form data
        username = self.validated_data['username']
        email = self.validated_data['email']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']

        #validation userform
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'error': 'Username already exists!'})
        if password != confirm_password:
            raise serializers.ValidationError({'error': 'Password does not match!'})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': 'Email already exists!'})

        #save userform
        user = User(username=username, email=email, first_name=first_name, last_name=last_name)
        user.is_active = False
        user.set_password(password)
        user.save()
        account_number = generate_unique_account_number()
        #save userprofile
        Profile.objects.create(
            user=user,
            phone_no=self.validated_data['phone_no'],
            account_no=account_number,
            account_type=self.validated_data['account_type'],
            birth_year=self.validated_data['birth_year'],
            birth_month=self.validated_data['birth_month'],
            birth_date=self.validated_data['birth_date'],
            gender=self.validated_data['gender'],
            zip_code=self.validated_data['zip_code'],
            city=self.validated_data['city'],
            state=self.validated_data['state'],
            country=self.validated_data['country'],
            street_address=self.validated_data['street_address'],
        )

        #email verification setup
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirm_link = f"{backend_link}/accounts/active/{uid}/{token}"
        mail_subject = "Please verify your email"
        mail_body = render_to_string('mail_confirm.html',
                                     {'confirm_link': confirm_link, 'account_number': account_number})
        send_mail = EmailMultiAlternatives(mail_subject, '', to=[user.email])
        send_mail.attach_alternative(mail_body, 'text/html')
        send_mail.send()


#user login serializer
class LoginSerializer(serializers.Serializer):
    account_no = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


#user balance update serialize
class BalanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['balance', 'account_no']


#user balance withdraw serialize
class BalanceWithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['balance', 'account_no', 'withdraw']


#user balance transfer serialize
class BalanceTransferSerializer(serializers.ModelSerializer):
    sender_account_no = serializers.CharField(required=True)
    receiver_account_no = serializers.CharField(required=True)

    class Meta:
        model = Profile
        fields = ['balance', 'sender_account_no', 'receiver_account_no']


#user passwrod change serializer
class PasswordChangeSerializer(serializers.Serializer):
    old_pass = serializers.CharField(required=True)
    new_pass = serializers.CharField(required=True)

    def validate_old_pass(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Old password does not match.")
        return value

    def validate_new_pass(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_pass'])
        user.save()


#profile image change serializer
class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image']


#transactions history
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


#loan requested serializers
class LoansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'


#Quick Transfer Serializers
class QuickTransferSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)
    receiver = UserProfileSerializer(read_only=True)

    class Meta:
        model = QuickTransfer
        fields = ['sender', 'receiver']

    def save(self):
        sender = self.context['request'].user
        receiver_id = self.context['request'].data.get('account')
        receiver = Profile.objects.get(account_no=receiver_id).user
        quick_transfer = QuickTransfer.objects.create(sender=sender, receiver=receiver)
        return quick_transfer
