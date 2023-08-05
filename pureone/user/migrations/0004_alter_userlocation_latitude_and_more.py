# Generated by Django 4.2.2 on 2023-07-26 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_userlocation_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlocation',
            name='latitude',
            field=models.DecimalField(decimal_places=24, max_digits=27),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='longitude',
            field=models.DecimalField(decimal_places=24, max_digits=27),
        ),
    ]
