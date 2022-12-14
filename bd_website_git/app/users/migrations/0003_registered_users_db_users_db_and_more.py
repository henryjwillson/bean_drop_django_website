# Generated by Django 4.1.2 on 2022-11-04 11:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_beandropprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='registered_users_db',
            fields=[
                ('idregistered_users_db', models.AutoField(primary_key=True, serialize=False)),
                ('EXTERNAL_ID', models.CharField(max_length=64, unique=True)),
                ('EXTERNAL_TYPE', models.CharField(max_length=16)),
            ],
            options={
                'db_table': 'registered_users_db',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='users_db',
            fields=[
                ('name_of_user', models.TextField()),
                ('user_email', models.CharField(max_length=255)),
                ('user_funds', models.DecimalField(decimal_places=4, max_digits=19)),
                ('cups_owned', models.IntegerField()),
                ('registration_date', models.DateTimeField()),
                ('POS_ID', models.IntegerField()),
                ('QR_generator', models.CharField(max_length=40)),
                ('POS_generator', models.CharField(max_length=40)),
                ('user_unique_ID', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('EXTERNAL_TYPE', models.CharField(max_length=16)),
                ('EXTERNAL_ID', models.CharField(max_length=64)),
                ('user_type', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'users_db',
                'managed': False,
            },
        ),
        migrations.RemoveField(
            model_name='beandropprofile',
            name='beandrop_qr_generator',
        ),
        migrations.AddField(
            model_name='profile',
            name='beandrop_cups_in_ownership',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='beandrop_number_of_cups_used',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='beandrop_social_user_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='beandrop_user_funds',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
