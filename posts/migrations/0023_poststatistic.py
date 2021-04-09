# Generated by Django 2.2.9 on 2021-04-05 20:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0022_auto_20210330_1917'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostStatistic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Дата')),
                ('views', models.IntegerField(default=0, verbose_name='Просмотры')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='posts.Post')),
            ],
        ),
    ]
