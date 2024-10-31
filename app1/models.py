from django.db import models 


# Create your models here.


#my "Users" model
class CreateUsers(models.Model):
    name=models.CharField(max_length=30,null=True)
    email=models.EmailField(max_length=60,unique=True,null=True)
    password=models.CharField(max_length=170,null=True)
    role=models.CharField(max_length=15,null=True)

    def __str__(self):
        return self.name

# Expense model

class NewExpense(models.Model):
    expenseid=models.AutoField(primary_key=True)
    expensename=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    location=models.CharField(max_length=100)
    date=models.DateField()
    user = models.ForeignKey(CreateUsers, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.expensename} - ${self.amount} on {self.date} by {self.user.name}"