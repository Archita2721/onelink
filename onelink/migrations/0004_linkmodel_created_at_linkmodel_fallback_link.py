# Generated by Django 4.1.5 on 2023-01-31 07:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('onelink', '0003_linkmodel_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='linkmodel',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='linkmodel',
            name='fallback_link',
            field=models.URLField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
