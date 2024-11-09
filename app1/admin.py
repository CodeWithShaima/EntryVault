from django.contrib import admin
from django.contrib.auth.models import User
from .models import NewExpense


#registering my NewExpense here
class ExpenseAdmin(admin.ModelAdmin):
     list_display = ['expensename', 'amount', 'location', 'date', 'user']

admin.site.register(NewExpense, ExpenseAdmin)