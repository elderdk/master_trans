# Generated by Django 3.1.2 on 2020-11-14 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0015_auto_20201109_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='seg_per_page',
            field=models.IntegerField(default=50),
        ),
    ]
