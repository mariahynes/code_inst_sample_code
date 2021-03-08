# Generated by Django 3.1.5 on 2021-02-09 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0030_auto_20210205_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('STRIPE', 'STRIPE'), ('PAYPAL', 'PayPal'), ('CASH', 'Cash'), ('FREE', 'Free')], max_length=6, verbose_name='Payment Method'),
        ),
    ]
