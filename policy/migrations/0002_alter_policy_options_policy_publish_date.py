# Generated by Django 5.1.3 on 2025-02-18 01:54

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policy', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='policy',
            options={'verbose_name': 'Policy', 'verbose_name_plural': 'Policies'},
        ),
        migrations.AddField(
            model_name='policy',
            name='publish_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
