# Generated by Django 3.1.5 on 2021-02-03 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_auto_20210203_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_reference',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Shipping Reference Number'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_posted_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date Posted/Delivered'),
        ),
    ]
