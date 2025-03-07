# Generated by Django 5.1.3 on 2024-11-15 01:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeHeroButton',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Subscribe', max_length=50)),
                ('link', models.CharField(default='/subscribe/', max_length=500)),
                ('template', models.CharField(choices=[('btn-primary', 'Primary'), ('btn-secondary', 'Secondary')], max_length=50)),
                ('home_page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='buttons', to='content.homepage')),
            ],
        ),
    ]
