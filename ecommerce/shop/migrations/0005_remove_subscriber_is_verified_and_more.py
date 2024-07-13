# Generated by Django 5.0.2 on 2024-07-10 19:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_subscriber'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriber',
            name='is_verified',
        ),
        migrations.RemoveField(
            model_name='subscriber',
            name='verification_code',
        ),
        migrations.AddField(
            model_name='subscriber',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
