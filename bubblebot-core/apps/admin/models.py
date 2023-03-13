from django.db import models
from django.contrib.auth.models import AbstractUser, Group


class Users(AbstractUser):

    user_status_choices = ((0, "禁用"), (1, "启用"))

    email = models.EmailField("用户邮箱", max_length=255, unique=True)
    username = models.CharField('用户姓名', max_length=32, unique=False)
    avatar = models.FileField('头像', upload_to='avatar/', null=True)
    user_status = models.IntegerField("用户状态", default=1, choices=user_status_choices)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    comment = models.CharField("备注", max_length=2048, null=True, blank=True)

    # 修改用户名字段为Email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # 删除默认无用字段
    first_name = None
    last_name = None
    last_login = None
    date_joined = None
    is_superuser = None
    is_staff = None

    class Meta:
        db_table = "admin_users"
        verbose_name_plural = "后台用户表"


class GroupExtra(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, primary_key=True)
    max_robot_num = models.IntegerField("可添加管理的机器人数量")
    comment = models.CharField("备注", max_length=2048, null=True, blank=True)

    class Meta:
        db_table = "auth_group_extra"
        verbose_name_plural = "组扩展字段表"


class Settings(models.Model):
    config_status_choices = ((0, "停用"), (1, "启用"))

    id = models.AutoField("参数ID", primary_key=True)
    config_name = models.CharField("参数名称", max_length=32)
    config_key = models.CharField("参数键名", max_length=48)
    config_value = models.CharField("参数键值", max_length=2048)
    config_status = models.IntegerField("配置状态", default=1, choices=config_status_choices)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "admin_settings"
        verbose_name_plural = "后台参数表"


class UserLoginLog(models.Model):
    login_result_choices = ((0, "成功"), (1, "失败"))
    id = models.AutoField("日志ID", primary_key=True)
    login_ip = models.CharField("登录IP", max_length=16)
    login_location = models.CharField("登录位置", max_length=32)
    login_time = models.DateTimeField("登录日期", auto_now_add=True)
    login_result = models.IntegerField("登录结果", choices=login_result_choices)

    login_user = models.ForeignKey(to="Users", to_field="email", on_delete=models.CASCADE)

    class Meta:
        db_table = "admin_user_loginlog"
        verbose_name_plural = "用户登录日志表"


class IpMapLocation(models.Model):
    binary_start_ip = models.CharField("二进制的起始IP段", max_length=32, null=False)
    binary_end_ip = models.CharField("二进制的结尾IP段", max_length=32, null=False)
    start_ip = models.CharField("起始IP段", max_length=16, null=False)
    end_ip = models.CharField("结尾IP段", max_length=16, null=False)
    location = models.CharField("IP位置", max_length=255, null=False)
    # seq_no，order_id，mac作为联合主键保证数据不重复
    class Meta:
        unique_together = (("binary_start_ip", "binary_end_ip"),)
        db_table = "ip_map_location"
        verbose_name_plural = "IP段与位置映射表"
