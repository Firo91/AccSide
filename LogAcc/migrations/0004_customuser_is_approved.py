# Generated by Django 4.2.6 on 2023-10-16 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LogAcc', '0003_customuser_role_alter_expense_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]