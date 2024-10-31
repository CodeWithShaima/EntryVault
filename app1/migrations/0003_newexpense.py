# Generated by Django 5.1.2 on 2024-10-31 10:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0002_rename_users_createusers'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewExpense',
            fields=[
                ('expenseid', models.AutoField(primary_key=True, serialize=False)),
                ('expensename', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('location', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app1.createusers')),
            ],
        ),
    ]
