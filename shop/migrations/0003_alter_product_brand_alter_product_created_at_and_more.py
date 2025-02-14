# Generated by Django 5.0.7 on 2025-01-19 13:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.CharField(db_index=True, max_length=20, verbose_name='brand'),
        ),
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.SmallIntegerField(blank=True, db_index=True, default=0, verbose_name='discount'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, default=1, max_digits=7, verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='reviewrating',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='reviewrating',
            name='rating',
            field=models.PositiveSmallIntegerField(db_index=True, default=0),
        ),
    ]
