# Generated by Django 3.2.8 on 2021-10-09 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aida', '0002_auto_20211009_0130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='vest_weight',
            field=models.FloatField(default=0),
        ),
    ]