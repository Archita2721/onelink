# Generated by Django 4.1.5 on 2023-02-01 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onelink', '0019_linkmodel_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='linkmodel',
            name='created_at',
        ),
    ]
