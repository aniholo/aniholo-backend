# Generated by Django 2.1.5 on 2019-02-14 09:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='post',
            table='posts',
        ),
        migrations.AlterModelTable(
            name='tag',
            table='tags',
        ),
        migrations.AlterModelTable(
            name='vote',
            table='votes',
        ),
    ]
