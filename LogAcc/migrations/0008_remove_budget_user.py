# Generated by Django 4.2.5 on 2023-09-11 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LogAcc', '0007_budgethistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='user',
        ),
    ]
