from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import UsersForm, NewExpenseForm
from django.contrib.auth.decorators import user_passes_test
from .models import NewExpense
from django.db.models import Sum

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




def UserDashboard(request):
    return render(request, 'UsersDashboard/user_dashboard.html')


@login_required
def ViewExpenses(request):
    # Render the view_expenses.html template
    expenses = NewExpense.objects.filter(user=request.user)
   
    return render(request, 'UsersDashboard/user_expenses.html', {'expenses': expenses})




#for user_dashboard adding expense function

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

    # Render the form again if the request method is GET or the form is not valid
    return render(request, 'UsersDashboard/user_addexpenses.html', {'form': form})







def ViewProfile(request):
    # Render the view_profile.html template
    user = request.user
    return render(request, 'UsersDashboard/user_profile.html', {'user': user})







def UserExpenseReport(request):
    # Render the userexpense_report.html template
    return render(request, 'UsersDashboard/userexpense_report.html')


###################################################################################################################

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
@login_required
def ExpenseReport(request):
    # Check if the user is an admin
    if request.user.is_staff:
        # Admin sees all expenses
        expenses = NewExpense.objects.all()
    else:
        # Regular user sees only their own expenses
        expenses = NewExpense.objects.filter(user=request.user)

    # Calculate tal_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    num_entries = expenses.count()
    
    return render(request, 'expensereport.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'num_entries': num_entries,
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

