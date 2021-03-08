# Generated by Django 3.1.5 on 2021-02-03 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0021_auto_20210203_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_discount_code',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Order Discount Code'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_posted',
            field=models.BooleanField(default=False, verbose_name='Order has been posted/delivered?'),
        ),
    ]