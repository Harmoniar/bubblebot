import yaml
from django import forms


class RobotQueryForm(forms.Form):
    robot_id_query = forms.IntegerField(
        label="机器人ID",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    robot_name_query = forms.CharField(
        label="机器人名称",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    master_id_query = forms.IntegerField(
        label="管理员ID",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    robot_status_query_choices = (("", ""), ("0", "停用"), ("1", "启用"))
    robot_status_query = forms.ChoiceField(
        label="机器人状态",
        choices=robot_status_query_choices,
        initial="",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    comment_query = forms.CharField(
        label="备注",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    page_index = forms.IntegerField(
        label="页面索引",
        required=True,
    )

    per_page_num_choices = (("10", "10"), ("50", "50"), ("100", "100"))
    per_page_num = forms.ChoiceField(
        label="页面索引",
        required=True,
        choices=per_page_num_choices,
    )


class RobotInsertForm(forms.Form):
    robot_id_insert = forms.CharField(
        label="机器人ID",
        required=True,
        max_length=11,
        min_length=5,
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "机器人ID"}),
        error_messages={"required": "机器人ID不能为空", "min_length": "机器人ID最小长度为5位", "max_length": "机器人ID最大长度为11位"},
    )

    robot_name_insert = forms.CharField(
        label="机器人名称",
        required=True,
        max_length=32,
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "机器人名称"}),
        error_messages={"required": "机器人名称不能为空", "max_length": "机器人名称最大长度为32位"},
    )

    master_id_insert = forms.CharField(
        label='管理员ID',
        required=False,
        help_text='可指定多个, 用"|"隔开',
        max_length=16384,
        error_messages={"max_length": "管理员ID最大长度为16384位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "管理员ID"}),
    )

    robot_status_choices = (("0", "停用"), ("1", "启用"))
    robot_status_insert = forms.ChoiceField(
        label="机器人状态",
        choices=robot_status_choices,
        initial="0",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    comment_insert = forms.CharField(
        label="备注",
        required=False,
        max_length=2048,
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "备注"}),
    )

    def clean_robot_id_insert(self):
        robot_id_insert: str = self.cleaned_data.get("robot_id_insert")
        if not robot_id_insert.isdigit():
            self.add_error("robot_id_insert", "机器人ID只能是数字")
        return robot_id_insert

    def clean_master_id_insert(self):
        field = qqid_in_list_verification(self, "master_id_insert", "管理员ID", "管理员QQ号", 5, 11)
        return field


# ==============================================================================================


class RobotUpdateForm(forms.Form):
    robot_id_update = forms.CharField(
        label="机器人ID",
        required=True,
        max_length=11,
        min_length=5,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "机器人ID"}),
        error_messages={"required": "机器人ID不能为空", "min_length": "机器人ID最小长度为5位", "max_length": "机器人ID最大长度为11位"},
    )

    robot_name_update = forms.CharField(
        label="机器人名称",
        required=True,
        max_length=32,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "机器人名称"}),
        error_messages={"required": "机器人名称不能为空", "max_length": "机器人名称最大长度为32位"},
    )

    master_id_update = forms.CharField(
        label='管理员ID',
        required=False,
        help_text='可指定多个, 用"|"隔开',
        max_length=16384,
        error_messages={"max_length": "管理员ID最大长度为16384位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "管理员ID"}),
    )

    robot_status_choices = (("0", "停用"), ("1", "启用"))
    robot_status_update = forms.ChoiceField(
        label="机器人状态",
        choices=robot_status_choices,
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control col-lg-7"}),
        error_messages={"required": "机器人状态不能为空"},
    )

    listen_msg_type_choices = (("1", "群组消息"), ("2", "好友消息"), ("3", "事件消息"))
    listen_msg_type_update = forms.MultipleChoiceField(
        label='监听消息类型',
        required=False,
        choices=listen_msg_type_choices,
        widget=forms.widgets.CheckboxSelectMultiple(attrs={"class": "custom-control-input"}),
    )

    protocol_server_mode_choices = (("0", "-"), ("1", "GO-CQHTTP"))
    protocol_server_mode_update = forms.ChoiceField(
        label="机器人协议端类型",
        choices=protocol_server_mode_choices,
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control col-lg-7"}),
    )

    protocol_server_config_update = forms.CharField(
        label="机器人协议端配置",
        required=False,
        help_text='必须为JSON/YAML格式',
        max_length=16384,
        error_messages={"max_length": "机器人协议端配置最大长度为16384位"},
        widget=forms.widgets.Textarea(attrs={"class": "form-control col-lg-7 hidden-scrollbar-textarea equal-width-font", "placeholder": "机器人协议端配置", "style": "height: 90px; border-radius: 1rem;"}),
    )

    trigger_mode_update_choices = (("1", "前缀命令"), ("2", "消息模板"))
    trigger_mode_update = forms.MultipleChoiceField(
        label='机器人触发方式',
        required=False,
        choices=trigger_mode_update_choices,
        widget=forms.widgets.CheckboxSelectMultiple(attrs={"class": "custom-control-input"}),
    )

    # 可同时指定多个
    command_prefix_update = forms.CharField(
        label='前缀触发指令',
        required=False,
        help_text='可指定多个, 用"|"隔开',
        max_length=16384,
        error_messages={"max_length": "前缀触发指令最大长度为16384位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "前缀触发指令"}),
    )

    # 可同时指定多个，指定的值为功能ID，另外特别的"all"代表除去管理员功能的其他所有功能
    user_function_permit_update = forms.CharField(
        label='用户功能权限',
        required=False,
        help_text='可指定多个, 用"|"隔开',
        max_length=16384,
        error_messages={"max_length": "用户功能权限最大长度为16384位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "全局用户功能权限"}),
    )

    group_permit_mode_choices = (("1", "白名单模式"), ("2", "黑名单模式"))
    group_permit_mode_update = forms.ChoiceField(
        label="群权限管理策略",
        choices=group_permit_mode_choices,
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control col-lg-7"}),
    )

    # 可同时指定多个
    group_whitelist_update = forms.CharField(
        label='群白名单',
        required=False,
        help_text='可指定多个, 用"|"隔开',
        max_length=16384,
        error_messages={"max_length": "群白名单最大长度为16384位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "群白名单"}),
    )

    group_blacklist_update = forms.CharField(
        label='群黑名单',
        required=False,
        help_text='可指定多个, 用"|"隔开',
        max_length=16384,
        error_messages={"max_length": "群黑名单最大长度为16384位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "群黑名单"}),
    )

    user_blacklist_update = forms.CharField(
        label='用户黑名单',
        required=False,
        help_text='可指定多个, 用"|"隔开',
        max_length=16384,
        error_messages={"max_length": "用户黑名单最大长度为16384位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "用户黑名单"}),
    )

    comment_update = forms.CharField(
        label="备注",
        required=False,
        max_length=2048,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "备注"}),
    )

    def clean_robot_id_update(self):
        robot_id_update: str = self.cleaned_data.get("robot_id_update")
        if not robot_id_update.isdigit():
            self.add_error("robot_id_update", "机器人ID只能是数字")
        return robot_id_update

    def clean_protocol_server_config_update(self):
        server_config = self.cleaned_data.get("protocol_server_config_update")
        if server_config:
            format_error = "机器人协议端配置的JSON/YAML格式错误, 请检查后重试"
            try:
                yaml_obj = yaml.safe_load(server_config)
                if not isinstance(yaml_obj, (dict, list)):
                    self.add_error("protocol_server_config_update", format_error)
            except Exception:
                self.add_error("protocol_server_config_update", format_error)
        return server_config

    def clean_master_id_update(self):
        field = qqid_in_list_verification(self, "master_id_update", "管理员ID", "管理员QQ号", 5, 11)
        return field

    def clean_user_blacklist_update(self):
        field = qqid_in_list_verification(self, "user_blacklist_update", "黑名单用户ID", "黑名单用户QQ号", 5, 11)
        return field

    def clean_group_blacklist_update(self):
        field = qqid_in_list_verification(self, "group_blacklist_update", "黑名单群ID", "黑名单QQ群号", 5, 11)
        return field

    def clean_group_whitelist_update(self):
        field = qqid_in_list_verification(self, "group_whitelist_update", "白名单群ID", "白名单QQ群号", 5, 11)
        return field


def qqid_in_list_verification(forms, field_name, field_label_1, field_label_2, min_len, max_len):
    field = forms.cleaned_data.get(field_name).strip(" |")
    if field:
        master_list = field.split("|")
        for i in master_list:
            i = i.strip()
            if not i.isdigit():
                forms.add_error(field_name, f"{field_label_1}格式错误, 请输入正确的{field_label_2}")
                break
            elif (len(i) < min_len) or (len(i) > max_len):
                forms.add_error(field_name, f"{field_label_1}格式错误, 该字段ID位数只能在{min_len}-{max_len}之间")
                break
    return field
