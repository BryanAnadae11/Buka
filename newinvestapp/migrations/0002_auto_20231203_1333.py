# Generated by Django 3.2 on 2023-12-03 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newinvestapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='contract_duration',
            field=models.FloatField(blank=True, default=180, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='investment_plan_name',
            field=models.CharField(blank=True, default='MISSED-INFO', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='running_days',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='payment_id',
            name='contract_duration',
            field=models.FloatField(blank=True, default=180, null=True),
        ),
        migrations.AddField(
            model_name='payment_id',
            name='investment_plan',
            field=models.FloatField(default=0.0052, null=True),
        ),
        migrations.AddField(
            model_name='payment_id',
            name='investment_plan_name',
            field=models.CharField(blank=True, default='MISSED-INFO', max_length=20, null=True),
        ),
    ]
