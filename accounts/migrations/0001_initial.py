# Generated by Django 4.2.13 on 2024-07-11 18:01

from django.conf import settings
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.CharField(max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator('^\\d{1,15}$')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('users', models.ManyToManyField(related_name='organisations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
