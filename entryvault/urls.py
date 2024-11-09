"""
URL configuration for entryvault project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.SignupPage, name='signup'),
    path('login/', views.LoginPage, name='login'), 
    path('home/', views.HomePage, name='home'),
    path('Logout/', views.LogoutPage, name='logout'),
    path('add-user/', views.adduser, name='adduser'),  

    path('expense/', views.Expense, name='expense'),  # Maps 'expense/' to expense view
    path('add-expense/', views.AddExpense, name='addexpense'),
    path('expense-report/', views.ExpenseReport, name='expensereport'),

    path('users/', views.Users, name='users'),
    path('delete/<int:id>', views.Delete_record, name='delete'),
    path('edit/<int:id>/', views.edit_user, name='edituser'),

    #User Dashboard
    path('user/dashboard/', views.UserDashboard, name='userdashboard'),
    path('user/view-expenses/', views.ViewExpenses, name='usersexpenses'),
    path('user/userexpense-report/', views.UserExpenseReport, name='usersexpensereport'),
]   
