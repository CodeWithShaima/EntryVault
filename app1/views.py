from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import usersform,NewExpenseForm
from .models import CreateUsers,NewExpense

# Create your views here.

@login_required(login_url='login')
def HomePage(request):
    return render (request,'home.html')


#this view takes the req of new user inserting form, that gets store in these variables
def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1!=pass2: 
            return HttpResponse("Passwords don't match!")
        else:
        
            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            usr = {"name": uname, "email": email, "role": "User", "password" : pass1}
            form = usersform(usr)
            form.save()
            return redirect('login')
       

    return render (request,'signup.html')


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
    
    form = usersform()
    data=CreateUsers.objects.all()

    context={
        'form' :form,
        'data' :data,
    }


    return render(request, 'users.html', context)



#adding users in the form 
def adduser(request):

    form = usersform()
    if request.method == 'POST':
        form = usersform(request.POST)  #on clicking post the data will be stored in variable named "form"
        if form.is_valid():
         form.save()
         form = usersform()
         return HttpResponse('user created succefully')
    else:
        form = usersform()
    return render(request, 'adduser.html', {'form': form}) 
        
#deleting user view
def Delete_record(request,id):
    a=CreateUsers.objects.get(pk=id)
    a.delete()
    return redirect('users')

#Edit user functionality
def edit_user(request, id):
    user = get_object_or_404(CreateUsers, id=id) 
    form = usersform(instance=user) #loding users data initially
    if request.method == 'POST': #if submitted, save
         form = usersform(request.POST, instance=user)  # Bind the form with the POST data
        #  form = usersform(request.POST, instance=user)
         if form.is_valid():
             form.save()
             return redirect('users')
        #  else:
        #   form = usersform(instance=user)

    return render(request, 'edituser.html', {'form':form, 'user': user})



 # expense table logic
def Expense(request): 

    expenses = NewExpense.objects.all()  # Retrieve all expense objects
    return render(request, 'expense.html', {'expenses': expenses}) 
    

#adding expense
def AddExpense(request):
    if request.method == 'POST':
     form = NewExpenseForm(request.POST)
     form.save()
     messages.success(request, "Expense added successfully!")
     return redirect('expense') 
    else:
        form = NewExpenseForm()
    return render(request, 'addexpense.html', {'form': form})

def LogoutPage(request):
    logout(request)
    return redirect('login')
