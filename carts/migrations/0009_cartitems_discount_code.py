# Generated by Django 3.1.5 on 2021-02-02 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0008_auto_20210202_0914'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitems',
            name='discount_code',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Discount Code'),
        ),
    ]
