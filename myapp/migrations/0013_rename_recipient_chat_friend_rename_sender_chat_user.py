# Generated by Django 5.0.2 on 2024-04-01 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_remove_friendship_receive_notifications_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='recipient',
            new_name='friend',
        ),
        migrations.RenameField(
            model_name='chat',
            old_name='sender',
            new_name='user',
        ),
    ]