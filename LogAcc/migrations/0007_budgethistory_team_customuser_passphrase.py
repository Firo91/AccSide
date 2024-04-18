# Generated by Django 4.2.5 on 2024-04-07 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LogAcc', '0006_remove_budget_team_budget_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgethistory',
            name='team',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='LogAcc.team'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customuser',
            name='passphrase',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
