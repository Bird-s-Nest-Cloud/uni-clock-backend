# Generated migration for Address model changes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_phone'),
    ]

    operations = [
        # Remove the old 'is_default' field
        migrations.RemoveField(
            model_name='address',
            name='is_default',
        ),
        # Remove the old 'both' choice from address_type
        migrations.AlterField(
            model_name='address',
            name='address_type',
            field=models.CharField(
                choices=[('billing', 'Billing'), ('shipping', 'Shipping')],
                default='shipping',
                max_length=20,
                verbose_name='Address Type'
            ),
        ),
        # Add new default fields
        migrations.AddField(
            model_name='address',
            name='is_default_billing',
            field=models.BooleanField(default=False, verbose_name='Default Billing Address'),
        ),
        migrations.AddField(
            model_name='address',
            name='is_default_shipping',
            field=models.BooleanField(default=False, verbose_name='Default Shipping Address'),
        ),
        # Add new constraints
        migrations.AddConstraint(
            model_name='address',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_default_billing', True)),
                fields=('user', 'address_type', 'is_default_billing'),
                name='unique_default_billing_per_user'
            ),
        ),
        migrations.AddConstraint(
            model_name='address',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_default_shipping', True)),
                fields=('user', 'address_type', 'is_default_shipping'),
                name='unique_default_shipping_per_user'
            ),
        ),
    ]
