# Generated by Django 4.1.2 on 2022-11-04 11:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20221104_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='beandrop_social_user_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
