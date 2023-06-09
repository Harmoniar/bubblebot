# Generated by Django 3.2.13 on 2022-08-07 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0006_auto_20220807_0029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='components',
            name='errors',
            field=models.JSONField(default=dict, verbose_name='错误信息: Dict'),
        ),
        migrations.AlterField(
            model_name='functions',
            name='default_command_args',
            field=models.JSONField(default=list, verbose_name='默认触发命令的参数: List[Dict]'),
        ),
        migrations.AlterField(
            model_name='functions',
            name='default_exception_template',
            field=models.JSONField(default=dict, verbose_name='默认排除模板: Dict'),
        ),
        migrations.AlterField(
            model_name='functions',
            name='default_trigger_command',
            field=models.JSONField(default=list, verbose_name='默认前缀触发使用的命令: List[str]'),
        ),
        migrations.AlterField(
            model_name='functions',
            name='default_trigger_template',
            field=models.JSONField(default=dict, verbose_name='默认触发模板: Dict'),
        ),
        migrations.AlterField(
            model_name='robot2function',
            name='command_args',
            field=models.JSONField(default=list, verbose_name='触发命令的参数: List[Dict]'),
        ),
        migrations.AlterField(
            model_name='robot2function',
            name='exception_template',
            field=models.JSONField(default=dict, verbose_name='排除模板: Dict'),
        ),
        migrations.AlterField(
            model_name='robot2function',
            name='trigger_command',
            field=models.JSONField(default=list, verbose_name='前缀触发使用的命令: List[str]'),
        ),
        migrations.AlterField(
            model_name='robot2function',
            name='trigger_template',
            field=models.JSONField(default=dict, verbose_name='触发模板: Dict'),
        ),
    ]
