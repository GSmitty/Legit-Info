# Generated by Django 3.0.8 on 2020-08-08 23:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fixpol', '0016_auto_20200808_2031'),
    ]

    operations = [
        migrations.RenameField(
            model_name='law',
            old_name='impacts',
            new_name='impact',
        ),
    ]