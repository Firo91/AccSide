# Generated by Django 4.2.5 on 2024-04-02 22:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LogAcc', '0002_customuser_current_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budgethistory',
            old_name='er',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='buttonpresslog',
            old_name='er',
            new_name='user',
        ),
    ]