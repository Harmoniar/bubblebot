# Generated by Django 3.2.13 on 2022-08-14 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0014_alter_robot2function_command_args'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robot2function',
            name='command_args',
            field=models.JSONField(default=list, verbose_name='触发命令的参数: List[Dict]'),
        ),
    ]
