# Generated by Django 3.2 on 2025-03-30 11:16

import django.core.validators
from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20250329_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[reviews.validators.validate_username_contains_me, django.core.validators.RegexValidator(code='invalid_username', message='Username must match the pattern.', regex='^[\\w.@+-]+')], verbose_name='Имя пользователя'),
        ),
    ]
