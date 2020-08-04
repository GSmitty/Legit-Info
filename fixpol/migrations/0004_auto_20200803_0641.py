# Generated by Django 3.0.8 on 2020-08-03 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixpol', '0003_location_hierarchy'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='govlevel',
            field=models.CharField(default='city', max_length=80),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='location',
            name='hierarchy',
            field=models.CharField(max_length=200),
        ),
    ]