# Generated by Django 2.2.3 on 2019-07-21 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocks',
            name='time_series',
            field=models.CharField(default='intraday', max_length=100),
        ),
    ]