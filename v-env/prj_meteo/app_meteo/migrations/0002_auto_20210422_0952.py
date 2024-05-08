# Generated by Django 3.1.6 on 2021-04-22 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_meteo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='In_temp',
            fields=[
                ('CollectInfoID', models.AutoField(default=None, primary_key=True, serialize=False)),
                ('collectdate', models.DateTimeField()),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=5)),
                ('humidity', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                'db_table': 'weather_indoor',
                'ordering': ['collectdate'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Out_temp',
            fields=[
                ('CollectInfoID', models.AutoField(default=None, primary_key=True, serialize=False)),
                ('collectdate', models.DateTimeField()),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=5)),
                ('humidity', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                'db_table': 'weather_outdoor',
                'ordering': ['collectdate'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Serre_temp',
            fields=[
                ('CollectInfoID', models.AutoField(default=None, primary_key=True, serialize=False)),
                ('collectdate', models.DateTimeField()),
                ('temperature', models.DecimalField(decimal_places=2, max_digits=5)),
                ('humidity', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                'db_table': 'weather_serre',
                'ordering': ['collectdate'],
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='TempData',
        ),
    ]
