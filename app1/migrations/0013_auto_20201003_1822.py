# Generated by Django 2.2 on 2020-10-03 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0012_auto_20201003_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_image',
            field=models.ImageField(blank=True, default='', upload_to='images/'),
        ),
    ]
