from django.forms import ModelForm
from .models import CreateUsers,NewExpense
from django import forms
from django.forms import Widget


class usersform(ModelForm):
    class Meta:
        model=CreateUsers
        fields='__all__'

        widgets={
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'email':forms.TextInput(attrs={'class':'form-control'}),
            'role':forms.TextInput(attrs={'class':'form-control'}),
            'password':forms.PasswordInput(attrs={'class':'form-control'},render_value=True)
            
        }


class NewExpenseForm(forms.ModelForm):
    class Meta:
        model = NewExpense
        fields = ['expensename', 'amount', 'location', 'date', 'user']
        widgets = {
            'expensename': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
        }