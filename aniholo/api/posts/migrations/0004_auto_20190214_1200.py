# Generated by Django 2.1.5 on 2019-02-14 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20190214_1001'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostTag',
            fields=[
                ('tag_id', models.AutoField(primary_key=True, serialize=False)),
                ('tag_value', models.TextField(unique=True)),
            ],
            options={
                'db_table': 'tagz',
            },
        ),
        migrations.CreateModel(
            name='PostTagPivot',
            fields=[
                ('post_id', models.IntegerField(primary_key=True, serialize=False)),
                ('tag_id', models.IntegerField()),
            ],
            options={
                'db_table': 'post_tag_pivot',
            },
        ),
        migrations.RemoveField(
            model_name='tag',
            name='post',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
