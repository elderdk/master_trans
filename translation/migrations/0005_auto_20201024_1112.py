# Generated by Django 3.1.2 on 2020-10-24 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0004_auto_20201021_1348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segment',
            name='id',
            field=models.AutoField(default=1, primary_key=True, serialize=False),
        ),
    ]
