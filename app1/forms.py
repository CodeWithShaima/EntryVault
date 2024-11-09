from django import forms
from django.contrib.auth.models import User
from .models import NewExpense 


class UsersForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email','password']  # Adjust as necessary

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
        return user


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