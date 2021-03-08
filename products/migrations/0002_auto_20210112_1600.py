# Generated by Django 3.1.5 on 2021-01-12 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_price',
            field=models.DecimalField(decimal_places=2, default=45, max_digits=6, verbose_name='Price'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='product_price_currency',
            field=models.CharField(default='EUR', max_length=3, verbose_name='Price Currency'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_display_name',
            field=models.CharField(max_length=255, verbose_name='Name of Product'),
        ),
    ]
