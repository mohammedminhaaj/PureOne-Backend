# Generated by Django 4.2.2 on 2023-07-14 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_cart_cart_unique_user_product_quantity_mapping'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='cart',
            name='unique_user_product_quantity_mapping',
        ),
        migrations.RenameField(
            model_name='cart',
            old_name='quantity',
            new_name='product_quantity',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='product',
        ),
        migrations.AddConstraint(
            model_name='cart',
            constraint=models.UniqueConstraint(fields=('user', 'product_quantity'), name='unique_user_product_quantity_mapping'),
        ),
    ]
