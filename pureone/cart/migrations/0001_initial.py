# Generated by Django 4.2.2 on 2023-08-06 17:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_count', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, message="Quantity count can't be less than 1"), django.core.validators.MaxValueValidator(10, message="Quantity count can't be greater than 10")], verbose_name='Quantity Count')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified At')),
            ],
            options={
                'verbose_name': 'Cart',
                'verbose_name_plural': 'Cart',
                'db_table': 'cart',
                'ordering': ['-id'],
            },
        ),
    ]
