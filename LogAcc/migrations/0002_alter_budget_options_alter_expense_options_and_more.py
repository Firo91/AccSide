# Generated by Django 4.2.5 on 2023-09-10 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('LogAcc', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='budget',
            options={'permissions': [('can_set_budget_for_others', 'Can set budget for other users')]},
        ),
        migrations.AlterModelOptions(
            name='expense',
            options={'permissions': [('export_all_users', 'Can export expenses for all users')]},
        ),
        migrations.AddField(
            model_name='budget',
            name='date_set',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='budget',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
