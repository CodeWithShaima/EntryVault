from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import UsersForm, NewExpenseForm
from django.contrib.auth.decorators import user_passes_test
from .models import NewExpense
#from django.http import JsonResponse

from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def HomePage(request):
     user_name = request.user.username
     return render(request, 'home.html', {'user_name': user_name})


def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Passwords don't match!")
        
        if User.objects.filter(email=email).exists():
            return HttpResponse("User  with this email already exists!")

        my_user = User.objects.create_user(username=uname, email=email, password=pass1)
        my_user.save()
        return redirect('login')

    return render(request, 'signup.html')

#  return render (request,'login.html')

def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')  # Changed variable name to 'password' for clarity
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!') 
            if user.is_superuser:
                return redirect('home') 
            else:
                return redirect('user_dashboard')  # Redirect to user dashboard for regular users
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')  


##########################################################################################################################


def UserDashboard(request):
    return render(request, 'UsersDashboard/user_dashboard.html')



#this shows the expense list in users portal
@login_required
def ViewExpenses(request):
    expenses = NewExpense.objects.filter(user=request.user)
    return render(request, 'UsersDashboard/user_expenses.html', {'expenses': expenses})



#through this user can add expense in the users portal
@login_required
def user_addexpense(request):
    if request.method == 'POST':
        form = NewExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('user_dashboard')  # Redirect to user dashboard after saving
    else:
        form = NewExpenseForm()  # Initialize the form for GET request
    return render(request, 'UsersDashboard/user_addexpenses.html', {'form': form})

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(NewExpense, expenseid=expense_id)
    if request.method == 'POST':
        form = NewExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('user_expenses')  # Redirect to the correct URL for the expense list page
    else:
        form = NewExpenseForm(instance=expense)
    return render(request, 'user_editexpenses.html', {'form': form})



@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(NewExpense, expenseid=expense_id)
    
    if request.method == 'POST':  # Confirming the delete action
        expense.delete()
        return redirect('user_expense')  # Redirect to the list of expenses

    return render(request, 'confirm_delete.html', {'expense': expense})





def UserExpenseReport(request):
    return render(request, 'UsersDashboard/userexpense_report.html')

def ViewProfile(request):
    user = request.user
    return render(request, 'UsersDashboard/user_profile.html', {'user': user})

###############################################################################################################################################

#ADMINS PORTAL 

#getting users list in admin page
def Users(request):
    
    if not request.user.is_superuser:
        return redirect('home')
    form = UsersForm()
    data=User.objects.all()
    context={
        'form' :form,
        'data' :data,
    }
    return render(request, 'users.html', context)


# adding users through admin portal
def admin_required(function):
    return user_passes_test(lambda u: u.is_superuser)(function)

@admin_required
def adduser(request):
    if request.method == 'POST':  # Check if the form was submitted

        form = UsersForm(request.POST)  # Populate the form with the submitted data
        if form.is_valid(): 
                print("Form is valid")
            # Check if a user with this email already exists
                if User.objects.filter(email=form.cleaned_data['email']).exists():
                    return HttpResponse("User  with this email already exists!")
                form.save()
                return redirect('users')  # Redirect to the users list or another page
        else:
            print("Form errors:", form.errors) 
    else:
        form = UsersForm()  # Create a new empty form
    
    return render(request, 'adduser.html', {'form': form})  # Ensure the template name is correct


#deleting user in urs list in admin portal
def Delete_record(request,id):
    a=User.objects.get(pk=id)
    a.delete()
    return redirect('users')



#Editing users in admin portal
def edit_user(request, id):
    user = get_object_or_404(User, id=id) 
    form = UsersForm(instance=user) #loding users data initially
    if request.method == 'POST': #if submitted, save
         form = UsersForm(request.POST, instance=user)  # Bind the form with the POST data
         if form.is_valid():
             form.save()
             return redirect('users')
    return render(request, 'edituser.html', {'form':form, 'user': user})

#####################################################################################################################################################

#expenselist funtion
@login_required
def Expense(request):
    if request.user.is_superuser:
        expenses = NewExpense.objects.all()
    else:    
        expenses = NewExpense.objects.filter(user=request.user)

    return render(request, 'expense.html', {'expenses': expenses} )


#add user expense in admin portal
@login_required
def AddExpense(request):
    form = NewExpenseForm()
    if request.method == 'POST':
        form =  NewExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            form.save()
            messages.success(request, 'Expense added successfully!')
            return redirect ('home')
    else:
            expenses = NewExpense.objects.all()  # Fetch existing expenses
    return render(request, 'addexpense.htmt', {'form': form, 'expenses': expenses})




#expense report in admin portal
# @login_required
# def ExpenseReport(request):
        
#     expenses = NewExpense.objects.all()
#     total_expenses = int(expenses.aggregate(Sum('amount'))['amount__sum'] or 0)
#     num_entries = expenses.count()
#     num_employees = NewExpense.objects.count()
#     expense_per_employee = int(total_expenses / num_employees) if num_employees > 0 else 0
   
#     return render(request, 'expensereport.html', {
#         'expenses': expenses,
#         'total_expenses': total_expenses,
#         'num_entries': num_entries,
#         'num_employees': num_employees,
#         'expense_per_employee': expense_per_employee,
#     })

@login_required
def ExpenseReport(request):
    # Query all expenses
    expenses = NewExpense.objects.all()

    # Calculate total expenses
    total_expenses = int(expenses.aggregate(Sum('amount'))['amount__sum'] or 0)

    # Get total number of expenses (entries) and total number of unique users
    num_entries = expenses.count()
    num_employees = User.objects.count()  # Assuming all users are employees

    # Average expense per employee
    expense_per_employee = int(total_expenses / num_employees) if num_employees > 0 else 0

    # Calculate expenses for the current month
    current_month = timezone.now().month
    current_year = timezone.now().year
    current_month_expenses = expenses.filter(date__month=current_month, date__year=current_year)
    total_current_month_expenses = int(current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0)
    average_current_month_expense = int(total_current_month_expenses / num_employees) if num_employees > 0 else 0

    return render(request, 'expensereport.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'num_entries': num_entries,
        'num_employees': num_employees,
        'expense_per_employee': expense_per_employee,
        'total_current_month_expenses': total_current_month_expenses,
        'average_current_month_expense': average_current_month_expense,
        'current_month': current_month,      # Add this
        'current_year': current_year, 
    })

@login_required
def MonthlyExpenseReport(request):
    # Get the month and year from query parameters (e.g., ?month=10&year=2024)
    month = request.GET.get('month')
    year = request.GET.get('year')

    if month and year:
        monthly_expenses = NewExpense.objects.filter(date__month=month, date__year=year)
        total_monthly_expenses = int(monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0)
    else:
        monthly_expenses = NewExpense.objects.none()  # Empty queryset if no month or year
        total_monthly_expenses = 0

    return render(request, 'monthlyexpensereport.html', {
        'monthly_expenses': monthly_expenses,
        'total_monthly_expenses': total_monthly_expenses,
        'month': month,
        'year': year,
    })

#logout logic
def LogoutPage(request):
        logout(request)
        return redirect('login')





















# #for user_dashboard adding expense function
# @login_required
# def user_addexpense(request):
#     form=NewExpenseForm()
#     if request.method == 'POST':
#         form=NewExpenseForm(request.POST)
#         if form.is_valid():
#             expense = form.save(commit=False)
#             expense.user = request.user
#             expense.save()
#             messages.success(request, 'Expense added successfully!')
#             return redirect('user_dashboard')   
#     return redirect(request, 'user_editexpenses.html' , {'form:form'})

