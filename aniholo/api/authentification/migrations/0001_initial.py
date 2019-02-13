# Generated by Django 2.1.5 on 2019-02-13 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('email', models.TextField()),
                ('date_joined', models.IntegerField()),
                ('last_login', models.IntegerField()),
                ('secret', models.CharField(max_length=32)),
                ('user_ip', models.CharField(max_length=15)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
    ]
