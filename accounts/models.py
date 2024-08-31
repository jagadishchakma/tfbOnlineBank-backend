from django.db import models
from django.contrib.auth.models import User


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcations')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)
    type = models.CharField(max_length=250)
    read = models.BooleanField(default=False)
    message = models.TextField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='accounts/images/', default='accounts/images/default_profile.png')
    street_address = models.CharField(max_length=200, null=True, blank=True)
    phone_no = models.IntegerField(null=True, blank=True)
    balance = models.IntegerField(default=0.0)
    deposit = models.IntegerField(default=0.0)
    withdraw = models.IntegerField(default=0.0)
    transfer = models.IntegerField(default=0.0)
    loan = models.IntegerField(default=0.0)
    account_no = models.CharField(max_length=12)
    account_type = models.CharField(max_length=50)
    birth_year = models.IntegerField(null=True, blank=True)
    birth_month = models.IntegerField(null=True, blank=True)
    birth_date = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username


#loan request
class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)
    status = models.BooleanField(default=False)
    pay = models.BooleanField(default=False)


#Quick Transfer
class QuickTransfer(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', unique=False)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver', unique=False)
