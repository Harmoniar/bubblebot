import json
from django.db import models


class Robots(models.Model):
    admin_user = models.ForeignKey(to="admin.Users", to_field="email", on_delete=models.CASCADE)
    robot_id = models.BigIntegerField("机器人QQID", unique=True)

    robot_name = models.CharField("机器人名称", max_length=32)

    # MasterId可有多个
    master_id = models.JSONField("机器人管理员QQID: List[int]", default=list)

    robot_status_choices = ((0, "停用"), (1, "启用"))
    robot_status = models.IntegerField("机器人状态", default=0, choices=robot_status_choices)

    start_time = models.DateTimeField("启用时间", null=True)

    protocol_server_mode_choices = ((0, "-"), (1, "GO-CQHTTP"))
    protocol_server_mode = models.IntegerField("机器人协议端类型", choices=protocol_server_mode_choices, default=0, null=True)
    protocol_server_config = models.JSONField("机器人协议端配置: Dict", default=dict)

    # 可同时指定多个 1.群消息  2.好友消息  3.事件消息
    listen_msg_type = models.JSONField("机器人监听的消息类型: List[int]", default=list)

    # 可同时指定多个 1.前缀命令方式触发  2.消息模板方式触发
    trigger_mode = models.JSONField("机器人触发方式: List[int]", default=list)
    command_prefix = models.JSONField("前缀触发命令的前缀: List[str]", default=list)

    # 指定的值为功能ID，另外特别的"all"代表除去管理员功能的其他所有功能
    user_function_permit = models.JSONField("用户功能权限: List[str]", default=list)

    group_permit_mode_choices = ((1, "白名单模式"), (2, "黑名单模式"))
    group_permit_mode = models.IntegerField("群权限管理模式", default=1, choices=group_permit_mode_choices)
    group_whitelist = models.JSONField("群白名单:List[int]", default=list)
    group_blacklist = models.JSONField("群黑名单: List[int]", default=list)

    # 如果进到用户黑名单，则无论是群消息还是私聊消息都会屏蔽
    user_blacklist = models.JSONField("用户黑名单: List[int]", default=list)

    comment = models.CharField("备注", max_length=2048, null=True)

    class Meta:
        unique_together = (("admin_user", "robot_id"),)
        db_table = "robots"
        verbose_name_plural = "机器人表"


class Functions(models.Model):

    function_id = models.CharField("功能ID", max_length=32, primary_key=True)
    function_name = models.CharField("功能名称", max_length=32)
    function_url = models.CharField("功能路径", max_length=255)

    # 例如：功能分为admin类、translate类、emoticon类等，或者不分类也行
    function_class = models.CharField("功能分类", max_length=32, null=True)

    # 此处的功能状态优先于用户自己设定的
    global_function_status_choices = ((0, "停用"), (1, "启用"))
    global_function_status = models.IntegerField("功能状态", default=1, choices=global_function_status_choices)

    # 默认的功能配置，仅用来提供给FunctionSettings做默认值
    default_trigger_command = models.JSONField("默认前缀触发使用的命令: List[str]", default=list)
    default_command_args = models.JSONField("默认触发命令的参数: List[Dict]", default=list)
    default_trigger_template = models.JSONField("默认触发模板: Dict", default=dict)
    default_exception_template = models.JSONField("默认排除模板: Dict", default=dict)

    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    explain = models.CharField("功能说明", max_length=2048, null=True)

    class Meta:
        db_table = "functions"
        verbose_name_plural = "机器人功能表"


class Robot2Function(models.Model):
    admin_user = models.ForeignKey(to="admin.Users", to_field="email", on_delete=models.CASCADE)
    robot = models.ForeignKey(to="Robots", to_field="robot_id", on_delete=models.CASCADE)
    function = models.ForeignKey(to="Functions", to_field="function_id", on_delete=models.CASCADE)

    function_status_choices = ((0, "停用"), (1, "启用"))
    function_status = models.IntegerField("功能状态", default=1, choices=function_status_choices)

    # ["command1", "command2"]
    trigger_command = models.JSONField("前缀触发使用的命令: List[str]", default=list)

    # [{"option": [str, ...], "dest": "...", "default": "...", "explain": "...", "action": "store"}, ...]
    command_args = models.JSONField("触发命令的参数: List[Dict]", default=list)

    # {"template_regexp": ["args_name1", "args_name2"]}
    trigger_template = models.JSONField("触发模板: Dict", default=dict)
    exception_template = models.JSONField("排除模板: Dict", default=dict)

    class Meta:
        unique_together = (("admin_user_id", "robot_id", "function_id"),)
        db_table = "robot2function"
        verbose_name_plural = "机器人与功能关系表"


class TimingFunctions(models.Model):
    timing_function_id = models.CharField("定时任务功能ID", max_length=32, primary_key=True)
    timing_function_name = models.CharField("功能名称", max_length=32)
    timing_function_url = models.CharField("功能路径", max_length=255)

    # 例如：功能分为admin类、translate类、emoticon类等，或者不分类也行
    timing_function_class = models.CharField("功能分类", max_length=32, null=True)

    # 此处的功能状态优先于用户自己设定的
    global_function_status_choices = ((0, "停用"), (1, "启用"))
    global_function_status = models.IntegerField("功能状态", default=1, choices=global_function_status_choices)

    # 默认的功能配置，仅用来提供做默认值
    default_timing_cron = models.CharField("默认定时时间", max_length=255)

    # 默认的功能配置，仅用来提供做默认值
    default_function_config = models.JSONField("默认定时任务功能配置: Dict", default=list)

    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    explain = models.CharField("定时功能说明", max_length=2048, null=True)

    class Meta:
        db_table = "timing_functions"
        verbose_name_plural = "机器人定时功能表"


class Robot2Timing(models.Model):
    admin_user = models.ForeignKey(to="admin.Users", to_field="email", on_delete=models.CASCADE)
    robot = models.ForeignKey(to="Robots", to_field="robot_id", on_delete=models.CASCADE)
    timing_function = models.ForeignKey(to="TimingFunctions", to_field="timing_function_id", on_delete=models.CASCADE)
    timing_status_choices = ((0, "停用"), (1, "启用"))
    timing_status = models.IntegerField("功能状态", default=1, choices=timing_status_choices)
    timing_cron = models.CharField("定时任务时间", max_length=255, null=False)
    timing_function_config = models.JSONField("定时任务功能配置: Dict", default=dict)

    class Meta:
        unique_together = (("admin_user_id", "robot_id", "timing_function_id"),)
        db_table = "robot2timing"
        verbose_name_plural = "机器人与定时任务关系表"


class Components(models.Model):
    component_id = models.CharField("组件ID", max_length=64, primary_key=True)

    component_role_choices = ((1, "Messenger"), (2, "Processor"))
    component_role = models.IntegerField("组件角色", default=1, choices=component_role_choices)

    component_ip = models.CharField("组件IP", max_length=16)

    component_status_choices = ((0, "离线中"), (1, "运行中"))
    component_status = models.IntegerField("组件状态", choices=component_status_choices)

    running_msg = models.JSONField("运行信息: Dict", default=dict)

    last_report_time = models.DateTimeField("最近报告时间", null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "robot_component"
        verbose_name_plural = "机器人组件表"
