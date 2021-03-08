# Generated by Django 3.1.5 on 2021-02-18 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20210209_1402'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_image_sirv_2',
            field=models.URLField(blank=True, null=True, unique=True, verbose_name='Product Image Sirv 2'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_image_sirv_2_desc',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Product Image Sirv 1 Description'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_image_sirv_3',
            field=models.URLField(blank=True, null=True, unique=True, verbose_name='Product Image Sirv 3'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_image_sirv_3_desc',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Product Image Sirv 1 Description'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_image_sirv_4',
            field=models.URLField(blank=True, null=True, unique=True, verbose_name='Product Image Sirv 4'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_image_sirv_4_desc',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Product Image Sirv 1 Description'),
        ),
    ]
