# Generated by Django 3.1.2 on 2020-11-02 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0009_auto_20201102_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentenceparser',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sentence_parser', to='translation.project'),
        ),
    ]
