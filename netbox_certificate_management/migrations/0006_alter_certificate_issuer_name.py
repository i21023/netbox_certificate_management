# Generated by Django 5.0.7 on 2024-08-12 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_certificate_management', '0005_certificate_is_root'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='issuer_name',
            field=models.CharField(default=''),
            preserve_default=False,
        ),
    ]
