# Generated by Django 4.0.1 on 2022-05-22 09:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_reviews_createdat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviews',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='review', to='base.product'),
        ),
    ]
