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

    # return render (request,'home.html')

def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Passwords don't match!")

        # Check if a user with this email already exists
        if User.objects.filter(email=email).exists():
            return HttpResponse("User  with this email already exists!")

        # Create the user
        my_user = User.objects.create_user(username=uname, email=email, password=pass1)
        my_user.save()

        return redirect('login')

    return render(request, 'signup.html')

#login page controller
def LoginPage(request):
    if request.method=='POST':
     username=request.POST.get('username')  
     pass1=request.POST.get('pass')  
     user=authenticate(request,username=username,password=pass1)
     if user is not None:
         login(request,user)
         return redirect('home')
     else:
          
          render(request,'login.html',{'messg': 'Password is incorrect'})
        
     
    return render (request,'login.html')


#users page
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




# adding users in the form Custom decorator to check if the user is an admin

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


#deleting user view
def Delete_record(request,id):
    a=User.objects.get(pk=id)
    a.delete()
    return redirect('users')



#Edit user functionality
def edit_user(request, id):
    user = get_object_or_404(User, id=id) 
    form = UsersForm(instance=user) #loding users data initially
    if request.method == 'POST': #if submitted, save
         form = UsersForm(request.POST, instance=user)  # Bind the form with the POST data
         if form.is_valid():
             form.save()
             return redirect('users')
    return render(request, 'edituser.html', {'form':form, 'user': user})


#expenselist funtion
@login_required
def Expense(request):
    if request.user.is_superuser:
        expenses = NewExpense.objects.all()
    else:    
        expenses = NewExpense.objects.filter(user=request.user)

    return render(request, 'expense.html', {'expenses': expenses} )


#add user expense view

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
            return redirect ('expensereport')
    else:
            expenses = NewExpense.objects.all()  # Fetch existing expenses
    return render(request, 'addexpense.html', {'form': form, 'expenses': expenses})



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
