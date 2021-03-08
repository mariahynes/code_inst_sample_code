# Generated by Django 3.1.5 on 2021-01-18 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20210114_0925'),
        ('carts', '0004_auto_20210115_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='cart_items',
            field=models.ManyToManyField(through='carts.CartItems', to='products.Product'),
        ),
    ]
