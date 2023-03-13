# Generated by Django 3.2.15 on 2022-09-23 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0025_timingfunctions_default_timing_cron'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timingfunctions',
            options={'verbose_name_plural': '机器人定时功能表'},
        ),
        migrations.AlterField(
            model_name='timingfunctions',
            name='default_function_config',
            field=models.JSONField(default=list, verbose_name='默认定时任务功能配置: Dict'),
        ),
    ]