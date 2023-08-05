# Generated by Django 4.2.2 on 2023-07-27 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_userlocation_latitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlocation',
            name='latitude',
            field=models.DecimalField(decimal_places=16, max_digits=19),
        ),
        migrations.AlterField(
            model_name='userlocation',
            name='longitude',
            field=models.DecimalField(decimal_places=16, max_digits=19),
        ),
    ]
