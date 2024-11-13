from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import UsersForm, NewExpenseForm
from django.contrib.auth.decorators import user_passes_test
from .models import NewExpense
from django.http import JsonResponse
from django.db.models import Sum,Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import logging
from datetime import datetime
from django.db.models.functions import ExtractMonth


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
    return render(request, 'UsersDashboard/user_editexpense.html', {'form': form})



@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(NewExpense, expenseid=expense_id)
    expense.delete()
    return redirect('user_expenses')


#################################################################################

@login_required
def UserExpenseReport(request):
    user = request.user
    expense_name = request.GET.get('expense_name', '')
    location = request.GET.get('location', '')
    amount = request.GET.get('amount', '')  # Single amount field
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    expenses = NewExpense.objects.filter(user=user)

    if expense_name:
        expenses = expenses.filter(expensename__icontains=expense_name)
    if location:
        expenses = expenses.filter(location__icontains=location)
    if amount:
        expenses = expenses.filter(amount__exact=amount)  # Filter by exact amount
    if from_date:
        expenses = expenses.filter(date__gte=from_date)
    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Current month expenses
    current_month = timezone.now().month
    current_year = timezone.now().year
    current_month_expenses = expenses.filter(date__month=current_month, date__year=current_year)
    total_current_month_expenses = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Return JSON for AJAX or render for page load
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        expenses_data = list(expenses.values('expensename', 'location', 'amount', 'date'))
        return JsonResponse({
            'expenses': expenses_data,
            'total_expenses': total_expenses,
            'total_current_month_expenses': total_current_month_expenses,
        })

    return render(request, 'UsersDashboard/user_expensereport.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'total_current_month_expenses': total_current_month_expenses,
        'expense_name': expense_name,
        'location': location,
        'amount': amount,
        'from_date': from_date,
        'to_date': to_date,
    })



def UserExpenseAnalysis(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        analysis_type = request.GET.get('analysis_type')

        # Calculate expenses based on analysis type
        if analysis_type == 'monthly':
            # Group expenses by month
            expenses = Expense.objects.raw('SELECT SUM(amount) as total, EXTRACT(MONTH FROM date) as month FROM yourapp_expense GROUP BY month')
            labels = [f'Month {i+1}' for i in range(12)]
            data = [0] * 12  # Initialize data array for 12 months

            # Populate the data array with monthly expenses
            for expense in expenses:
                data[expense.month - 1] = expense.total  # Assign total for the month

            return JsonResponse({'labels': labels, 'data': data})

        elif analysis_type == 'yearly':
            # Group expenses by year
            expenses = Expense.objects.raw('SELECT SUM(amount) as total, EXTRACT(YEAR FROM date) as year FROM yourapp_expense GROUP BY year')
            labels = []
            data = []
            
            for expense in expenses:
                labels.append(str(expense.year))
                data.append(expense.total)

            return JsonResponse({'labels': labels, 'data': data})

        elif analysis_type == 'quarterly':
            # Group expenses by quarter
            expenses = Expense.objects.raw('SELECT SUM(amount) as total, EXTRACT(QUARTER FROM date) as quarter FROM yourapp_expense GROUP BY quarter')
            labels = ['Q1', 'Q2', 'Q3', 'Q4']
            data = [0] * 4  # Initialize data array for 4 quarters

            # Populate the data array with quarterly expenses
            for expense in expenses:
                data[expense.quarter - 1] = expense.total

            return JsonResponse({'labels': labels, 'data': data})

    return render(request, 'UsersDashboard/user_expenseanalysis.html')




def ViewProfile(request):
    user = request.user
    return render(request, 'UsersDashboard/user_profile.html', {'user': user})



###############################################################################################################################################

#ADMINS PORTAL 

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
    if request.method == 'POST': 
        form = UsersForm(request.POST) 
        if form.is_valid(): 
                print("Form is valid")
                if User.objects.filter(email=form.cleaned_data['email']).exists():
                    return HttpResponse("User  with this email already exists!")
                form.save()
                return redirect('home') 
    else:
        form = UsersForm()
        return render(request, 'adduser.html', {'form': form}) 


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


@login_required
def ExpenseReport(request):

      # Retrieve filter parameters
    user_name = request.GET.get('user_name', '')  
    expense_name = request.GET.get('expense_name', '')
    location = request.GET.get('location', '')
    amount = request.GET.get('amount', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    # Start with all expenses, filtering by user name if provided
    expenses = NewExpense.objects.all()

    if user_name:
        expenses = expenses.filter(user__username__icontains=user_name)
    if expense_name:
        expenses = expenses.filter(expensename__icontains=expense_name)
    if location:
        expenses = expenses.filter(location__icontains=location)
    if amount:
        expenses = expenses.filter(amount__exact=amount)
    if from_date:
        expenses = expenses.filter(date__gte=from_date)
    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    paginator = Paginator(expenses, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)    

    # Calculate total expenses and other aggregate values
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    num_entries = expenses.count()  # Total number of expense entries
    num_employees = expenses.values('user').distinct().count() 
    expense_per_employee = total_expenses / num_employees if num_employees else 0

    # Current month expenses
    current_month = timezone.now().month
    current_year = timezone.now().year
    current_month_expenses = expenses.filter(date__month=current_month, date__year=current_year)
    total_current_month_expenses = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    average_current_month_expense = current_month_expenses.aggregate(Avg('amount'))['amount__avg'] or 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        expenses_data = list(page_obj.object_list.values('user__username', 'expensename', 'location', 'amount', 'date'))
        return JsonResponse({
            'expenses': expenses_data,
            'total_expenses': total_expenses,
            'num_entries': num_entries,
            'num_employees': num_employees,
            'expense_per_employee': expense_per_employee,
            'total_current_month_expenses': total_current_month_expenses,
            'average_current_month_expense': average_current_month_expense,
            'current_month': current_month,
            'current_year': current_year,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        })


    # Render data for full page load
    return render(request, 'expensereport.html', {
        'page_obj': page_obj,
        'total_expenses': total_expenses,
        'num_entries': num_entries,
        'num_employees': num_employees,
        'expense_per_employee': expense_per_employee,
        'total_current_month_expenses': total_current_month_expenses,
        'average_current_month_expense': average_current_month_expense,
        'current_month': current_month,
        'current_year': current_year,
        'user_name': user_name,
        'expense_name': expense_name,
        'location': location,
        'amount': amount,
        'from_date': from_date,
        'to_date': to_date,
    })

logger = logging.getLogger(__name__)

@login_required
def ExpenseAnalysis(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        analysis_type = request.GET.get('analysis_type')

        if analysis_type == 'monthly':
            # Get monthly expenses grouped by month of the current year
            current_year = datetime.now().year
            expenses = (Expense.objects.filter(date__year=current_year)
                        .values('date__month')
                        .annotate(total=Sum('amount'))
                        .order_by('date__month'))
            
            labels = [f'Month {i+1}' for i in range(12)]
            data = [0] * 12  # Initialize data array for 12 months
            
            for expense in expenses:
                month_index = expense['date__month'] - 1  # Convert to zero-based index
                data[month_index] = expense['total']

            return JsonResponse({'labels': labels, 'data': data})

        elif analysis_type == 'yearly':
            # Get yearly expenses grouped by year
            expenses = (Expense.objects
                        .values('date__year')
                        .annotate(total=Sum('amount'))
                        .order_by('date__year'))
            
            labels = []
            data = []
            
            for expense in expenses:
                labels.append(str(expense['date__year']))
                data.append(expense['total'])

            return JsonResponse({'labels': labels, 'data': data})

        elif analysis_type == 'quarterly':
            # Get quarterly expenses grouped by quarter of the current year
            current_year = datetime.now().year
            expenses = (Expense.objects.filter(date__year=current_year)
                        .annotate(quarter=((ExtractMonth('date') - 1) // 3 + 1))
                        .values('quarter')
                        .annotate(total=Sum('amount'))
                        .order_by('quarter'))
            
            labels = ['Q1', 'Q2', 'Q3', 'Q4']
            data = [0] * 4  # Initialize data array for 4 quarters

            for expense in expenses:
                quarter_index = expense['quarter'] - 1  # Convert to zero-based index
                data[quarter_index] = expense['total']

            return JsonResponse({'labels': labels, 'data': data})

    # Default response to render the HTML template for non-AJAX GET requests
    return render(request, 'expenseanalysis.html')

#logout logic
def LogoutPage(request):
        logout(request)
        return redirect('login')

