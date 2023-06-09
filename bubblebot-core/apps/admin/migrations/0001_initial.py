# Generated by Django 3.2.13 on 2022-08-01 00:26

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='用户邮箱')),
                ('username', models.CharField(max_length=32, verbose_name='用户姓名')),
                ('avatar', models.FileField(default='default/avatar/default.jpg', upload_to='avatar/', verbose_name='头像')),
                ('user_status', models.IntegerField(choices=[(0, '禁用'), (1, '启用')], default=1, verbose_name='用户状态')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('comment', models.CharField(blank=True, max_length=2048, null=True, verbose_name='备注')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': '后台用户表',
                'db_table': 'admin_users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='GroupExtra',
            fields=[
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.group')),
                ('max_robot_num', models.IntegerField(verbose_name='可添加管理的机器人数量')),
                ('comment', models.CharField(blank=True, max_length=2048, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name_plural': '组扩展字段表',
                'db_table': 'auth_group_extra',
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='参数ID')),
                ('config_name', models.CharField(max_length=32, verbose_name='参数名称')),
                ('config_key', models.CharField(max_length=48, verbose_name='参数键名')),
                ('config_value', models.CharField(max_length=2048, verbose_name='参数键值')),
                ('config_status', models.IntegerField(choices=[(0, '停用'), (1, '启用')], default=1, verbose_name='配置状态')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name_plural': '后台参数表',
                'db_table': 'admin_settings',
            },
        ),
        migrations.CreateModel(
            name='UserLoginLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='日志ID')),
                ('login_ip', models.CharField(max_length=16, verbose_name='登录IP')),
                ('login_location', models.CharField(max_length=32, verbose_name='登录位置')),
                ('login_time', models.DateTimeField(auto_now_add=True, verbose_name='登录日期')),
                ('login_result', models.IntegerField(choices=[(0, '成功'), (1, '失败')], verbose_name='登录结果')),
                ('login_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='email')),
            ],
            options={
                'verbose_name_plural': '用户登录日志表',
                'db_table': 'admin_user_loginlog',
            },
        ),
        migrations.CreateModel(
            name='IpMapLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('binary_start_ip', models.CharField(max_length=32, verbose_name='二进制的起始IP段')),
                ('binary_end_ip', models.CharField(max_length=32, verbose_name='二进制的结尾IP段')),
                ('start_ip', models.CharField(max_length=16, verbose_name='起始IP段')),
                ('end_ip', models.CharField(max_length=16, verbose_name='结尾IP段')),
                ('location', models.CharField(max_length=255, verbose_name='IP位置')),
            ],
            options={
                'verbose_name_plural': 'IP段与位置映射表',
                'db_table': 'ip_map_location',
                'unique_together': {('binary_start_ip', 'binary_end_ip')},
            },
        ),
    ]
