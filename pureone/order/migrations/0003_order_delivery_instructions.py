# Generated by Django 4.2.2 on 2023-08-08 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_alter_order_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_instructions',
            field=models.TextField(blank=True, max_length=150, null=True, verbose_name='Delivery Instructions'),
        ),
    ]
