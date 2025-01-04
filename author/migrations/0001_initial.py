# Generated by Django 5.1.3 on 2024-12-26 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Jess Brown', help_text='Name as will be displayed on site and in schema', max_length=300)),
                ('bio', models.TextField(blank=True, default="<p>Designer turned developer with MS. I'm exploring the relationships between technology, humanity, and other systems. After my diagnosis of Multiple Sclerosis, I was forced to confront uncomfortable aspects of life: my queerness, my mortality, my limitations. I believe it is through the acceptance of both the good and the bad—healthy, unhealthy; productive, unproductive; safe, risky—we can find progress, peace, and potential.</p>")),
            ],
        ),
    ]
