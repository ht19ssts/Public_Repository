# Generated by Django 5.0.2 on 2024-03-10 15:30

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_healthcheck_notification'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='healthcheck_notification',
            new_name='HealthcheckNotification',
        ),
    ]