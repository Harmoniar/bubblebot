# Generated by Django 3.2.13 on 2022-08-07 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0008_alter_robots_trigger_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robots',
            name='master_id',
            field=models.JSONField(default=list, verbose_name='机器人管理员QQID: List[int]'),
        ),
    ]