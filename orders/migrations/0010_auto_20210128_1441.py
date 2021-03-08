# Generated by Django 3.1.5 on 2021-01-28 14:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_countryregion_postagerate_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='postagerate',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='postagerate',
            name='last_edited',
            field=models.DateTimeField(auto_now=True),
        ),
    ]