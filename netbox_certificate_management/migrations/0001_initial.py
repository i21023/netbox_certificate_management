# Generated by Django 5.0.7 on 2024-08-07 19:57

import django.db.models.deletion
import django.db.models.manager
import mptt.fields
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0187_alter_device_vc_position'),
        ('extras', '0115_convert_dashboard_widgets'),
        ('virtualization', '0038_virtualdisk'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('serial_number', models.DecimalField(decimal_places=0, max_digits=100)),
                ('signature_algorithm', models.CharField()),
                ('issuer_name', models.CharField(blank=True, null=True)),
                ('not_valid_before', models.DateTimeField()),
                ('not_valid_after', models.DateTimeField()),
                ('subject', models.CharField()),
                ('subject_public_key_algorithm', models.CharField()),
                ('subject_public_key', models.CharField()),
                ('extensions', models.JSONField(blank=True, default=dict, null=True)),
                ('comments', models.TextField(blank=True)),
                ('file', models.BinaryField()),
                ('_depth', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('devices', models.ManyToManyField(blank=True, related_name='certificates', to='dcim.device')),
                ('issuer', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='certificates', to='netbox_certificate_management.certificate')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('virtual_machines', models.ManyToManyField(blank=True, related_name='certificates', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'Certificate',
                'verbose_name_plural': 'Certificates',
            },
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
    ]
