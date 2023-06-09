# Generated by Django 3.2.13 on 2022-08-07 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0005_alter_robots_server_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robots',
            name='command_prefix',
            field=models.JSONField(default=list, verbose_name='前缀触发命令的前缀: List[str]'),
        ),
        migrations.AlterField(
            model_name='robots',
            name='group_blacklist',
            field=models.JSONField(default=list, verbose_name='群黑名单: List[int]'),
        ),
        migrations.AlterField(
            model_name='robots',
            name='group_whitelist',
            field=models.JSONField(default=list, verbose_name='群白名单:List[int]'),
        ),
        migrations.AlterField(
            model_name='robots',
            name='listen_msg_type',
            field=models.JSONField(default=list, verbose_name='机器人监听的消息类型: List[int]'),
        ),
        migrations.AlterField(
            model_name='robots',
            name='user_blacklist',
            field=models.JSONField(default=list, verbose_name='用户黑名单: List[int]'),
        ),
        migrations.AlterField(
            model_name='robots',
            name='user_function_permit',
            field=models.JSONField(default=list, verbose_name='用户功能权限: List[str]'),
        ),
    ]
