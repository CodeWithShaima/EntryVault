from django.db import models 
from django.contrib.auth.models import User


# Create your models here.
class NewExpense(models.Model):
    expenseid=models.AutoField(primary_key=True)
    expensename=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    location=models.CharField(max_length=100)
    date=models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate expense with user

    # def __str__(self):
    def __str__(self):
        return f"{self.expensename} - ${self.amount} on {self.date} by {self.user.username}"
