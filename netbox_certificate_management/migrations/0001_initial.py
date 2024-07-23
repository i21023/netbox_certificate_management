# Generated by Django 4.2.11 on 2024-07-19 18:28

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0185_gfk_indexes'),
        ('extras', '0107_cachedvalue_extras_cachedvalue_object'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('public_key', models.TextField()),
                ('issuer', models.CharField(max_length=100)),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('valid_to',),
            },
        ),
    ]