# Generated by Django 3.1.2 on 2020-10-19 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0002_auto_20201020_0712'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='uuid',
        ),
    ]
