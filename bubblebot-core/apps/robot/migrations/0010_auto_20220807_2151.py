# Generated by Django 3.2.13 on 2022-08-07 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0009_alter_robots_master_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robots',
            name='protocol_server_config',
            field=models.JSONField(default=dict, verbose_name='机器人协议端配置: Dict'),
        ),
        migrations.AlterField(
            model_name='robots',
            name='protocol_server_mode',
            field=models.IntegerField(choices=[(0, '-'), (1, 'GO-CQHTTP')], default=0, null=True, verbose_name='机器人协议端类型'),
        ),
    ]