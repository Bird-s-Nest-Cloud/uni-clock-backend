# Generated migration for CartItem model - add support for products without variants

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),  # Adjust based on your catalog migrations
        ('cart', '0001_initial'),
    ]

    operations = [
        # Add product field to CartItem
        migrations.AddField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(
                blank=True,
                help_text='Base product (for products without variants)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cart_items',
                to='catalog.product'
            ),
        ),
        # Make variant field optional
        migrations.AlterField(
            model_name='cartitem',
            name='variant',
            field=models.ForeignKey(
                blank=True,
                help_text='Product variant (for products with variants)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cart_items',
                to='catalog.productvariant'
            ),
        ),
        # Remove old unique_together constraint
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together=set(),
        ),
        # Add check constraint to ensure either variant or product is set
        migrations.AddConstraint(
            model_name='cartitem',
            constraint=models.CheckConstraint(
                check=(
                    models.Q(variant__isnull=False, product__isnull=True) |
                    models.Q(variant__isnull=True, product__isnull=False)
                ),
                name='cart_item_variant_or_product'
            ),
        ),
        # Add unique constraint for variant-based items
        migrations.AddConstraint(
            model_name='cartitem',
            constraint=models.UniqueConstraint(
                fields=['cart', 'variant'],
                condition=models.Q(variant__isnull=False),
                name='unique_cart_variant'
            ),
        ),
        # Add unique constraint for product-based items
        migrations.AddConstraint(
            model_name='cartitem',
            constraint=models.UniqueConstraint(
                fields=['cart', 'product'],
                condition=models.Q(product__isnull=False),
                name='unique_cart_product'
            ),
        ),
    ]
