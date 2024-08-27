from django.contrib import admin
from .models import Profile,Transaction

# Register your models here.
@admin.register(Profile)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','phone_no', 'balance']

@admin.register(Transaction)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ['id','user','type', 'amount','read']