from django import forms
from ..lib.verification import json_and_yaml_verification


class RobotFunctionQueryForm(forms.Form):

    robot_id_query = forms.CharField(
        label="机器人ID",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    function_id_query = forms.CharField(
        label="功能名称",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    function_status_query_choices = (("", ""), ("0", "停用"), ("1", "启用"))
    function_status_query = forms.ChoiceField(
        label="功能状态",
        choices=function_status_query_choices,
        initial="",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    trigger_command_query = forms.CharField(
        label='触发命令',
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    explain_query = forms.CharField(
        label="功能说明",
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


class RobotFunctionInsertForm(forms.Form):

    robot_id_insert = forms.CharField(
        label="机器人ID",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
        error_messages={"required": "机器人ID不能为空"},
    )

    function_id_insert = forms.CharField(
        label="功能名称",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
        error_messages={"required": "功能名称不能为空"},
    )

    function_status_insert_choices = (("0", "停用"), ("1", "启用"))
    function_status_insert = forms.ChoiceField(
        label="功能状态",
        choices=function_status_insert_choices,
        initial="0",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )


class RobotFunctionUpdateForm(forms.Form):

    robot_id_update = forms.CharField(
        label="机器人ID",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "disabled": "disabled"}),
    )

    function_id_update = forms.CharField(
        label="功能ID",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "disabled": "disabled"}),
    )

    function_status_update_choices = (("0", "停用"), ("1", "启用"))
    function_status_update = forms.ChoiceField(
        label="功能状态",
        choices=function_status_update_choices,
        initial="0",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control col-lg-7"}),
    )

    trigger_command_update = forms.CharField(
        label='触发命令',
        required=False,
        help_text='可指定多个, 用"|"隔开',
        max_length=16384,
        error_messages={"max_length": "触发命令最大长度为16384位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "前缀触发命令"}),
    )

    command_args_update = forms.CharField(
        label="触发命令参数",
        required=False,
        help_text='必须为JSON/YAML格式',
        max_length=16384,
        error_messages={"max_length": "触发命令参数最大长度为16384位"},
        widget=forms.widgets.Textarea(
            attrs={
                "class": "form-control col-lg-7 hidden-scrollbar-textarea equal-width-font",
                "placeholder": "触发命令参数",
                "style": "height: 120px; border-radius: 1rem;",
                "disabled": "disabled",
            }
        ),
    )

    trigger_template_update = forms.CharField(
        label="触发模板",
        required=False,
        help_text='必须为JSON/YAML格式',
        max_length=16384,
        error_messages={"max_length": "触发模板最大长度为16384位"},
        widget=forms.widgets.Textarea(
            attrs={"class": "form-control col-lg-7 hidden-scrollbar-textarea equal-width-font", "placeholder": "触发模板", "style": "height: 120px; border-radius: 1rem;"}
        ),
    )

    exception_template_update = forms.CharField(
        label="排除模板",
        required=False,
        help_text='必须为JSON/YAML格式',
        max_length=16384,
        error_messages={"max_length": "排除模板最大长度为16384位"},
        widget=forms.widgets.Textarea(
            attrs={"class": "form-control col-lg-7 hidden-scrollbar-textarea equal-width-font", "placeholder": "排除模板", "style": "height: 120px; border-radius: 1rem;"}
        ),
    )

    def clean_command_args_update(self):
        field = json_and_yaml_verification(self, "command_args_update")
        return field

    def clean_trigger_template_update(self):
        field = json_and_yaml_verification(self, "trigger_template_update")
        return field

    def clean_exception_template_update(self):
        field = json_and_yaml_verification(self, "exception_template_update")
        return field
