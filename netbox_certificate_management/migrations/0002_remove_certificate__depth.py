# Generated by Django 5.0.7 on 2024-08-07 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_certificate_management', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certificate',
            name='_depth',
        ),
    ]
