# Generated manually for Category description and image fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_alter_products_id_alter_productsimage_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.TextField(blank=True, null=True),
        ),
    ]
