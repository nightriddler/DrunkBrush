# Generated by Django 2.2.9 on 2021-03-27 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0015_auto_20210327_1935'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_follow',
        ),
    ]
