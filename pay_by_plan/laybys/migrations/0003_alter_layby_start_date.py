# Generated by Django 5.0.8 on 2024-10-22 09:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laybys', '0002_remove_layby_initial_payment_alter_layby_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layby',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Start date'),
        ),
    ]