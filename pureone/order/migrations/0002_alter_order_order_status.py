# Generated by Django 4.2.2 on 2023-08-07 04:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_delete_region'),
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.ForeignKey(limit_choices_to=models.Q(('master_category__name', 'Order Status')), on_delete=django.db.models.deletion.CASCADE, related_name='md_order_status', to='common.masterdata', verbose_name='Order Status'),
        ),
    ]
