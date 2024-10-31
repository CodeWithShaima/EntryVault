from django.contrib import admin
from .models import CreateUsers, NewExpense

# Register your models here.
class UsersAdmin(admin.ModelAdmin):
    list_display=['name','email','password','role']

admin.site.register(CreateUsers,UsersAdmin)

#registering my NewExpense here
class ExpenseAdmin(admin.ModelAdmin):
     list_display = ['expensename', 'amount', 'location', 'date', 'user']

admin.site.register(NewExpense, ExpenseAdmin)