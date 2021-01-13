# Generated by Django 3.1.2 on 2021-01-08 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20201118_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='expertise',
            field=models.ManyToManyField(blank=True, related_name='users', to='users.Expertise'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_client',
            field=models.BooleanField(blank=True, default=False, verbose_name='is_client'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.ManyToManyField(blank=True, to='users.Role'),
        ),
    ]