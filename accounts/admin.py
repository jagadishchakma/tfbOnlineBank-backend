from django.contrib import admin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Profile, Transaction, Loan, QuickTransfer


# Register your models here.
@admin.register(Profile)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone_no', 'balance']


@admin.register(Transaction)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'amount', 'read']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')

    def save_model(self, request, obj, form, change):
        if change:  # When updating an existing Loan object
            if obj.status:  # Check if the loan is being approved
                profile = obj.user.profile
                profile.loan += obj.amount
                profile.balance += obj.amount
                profile.save()
                # email verification setup
                user = obj.user
                mail_subject = "Loan Approved"
                message = f"Your Loan Approved successfully amount of ${obj.amount}."
                mail_body = render_to_string('loan_confirm.html', {'message': message})
                send_mail = EmailMultiAlternatives(mail_subject, '', to=[user.email])
                send_mail.attach_alternative(mail_body, 'text/html')
                send_mail.send()

                # save history
                Transaction.objects.create(
                    user=obj.user,
                    amount=obj.amount,
                    type='Loan',
                    message=f'Your Loan request approve successfully amount of ${obj.amount}'
                )

        super().save_model(request, obj, form, change)


#Quick Transfer
@admin.register(QuickTransfer)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver')

