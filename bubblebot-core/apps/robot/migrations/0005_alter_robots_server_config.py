# Generated by Django 3.2.13 on 2022-08-07 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0004_alter_robots_server_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robots',
            name='protocol_server_config',
            field=models.JSONField(default=dict, verbose_name='机器人服务端配置: Dict'),
        ),
    ]
