from django import forms
from ..lib.verification import json_and_yaml_verification


class RobotTimingQueryForm(forms.Form):

    robot_id_query = forms.CharField(
        label="机器人ID",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    timing_function_id_query = forms.CharField(
        label="定时功能名称",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    timing_status_query_choices = (("", ""), ("0", "停用"), ("1", "启用"))
    timing_status_query = forms.ChoiceField(
        label="定时任务状态",
        choices=timing_status_query_choices,
        initial="",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    explain_query = forms.CharField(
        label="定时功能说明",
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


class RobotTimingInsertForm(forms.Form):

    robot_id_insert = forms.CharField(
        label="机器人ID",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    timing_function_id_insert = forms.CharField(
        label="定时功能名称",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    timing_status_insert_choices = (("0", "停用"), ("1", "启用"))
    timing_status_insert = forms.ChoiceField(
        label="定时任务状态",
        choices=timing_status_insert_choices,
        initial="0",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )


class RobotTimingUpdateForm(forms.Form):

    robot_id_update = forms.CharField(
        label="机器人ID",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "disabled": "disabled"}),
    )

    timing_function_id_update = forms.CharField(
        label="定时功能ID",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "disabled": "disabled"}),
    )

    timing_status_update_choices = (("0", "停用"), ("1", "启用"))
    timing_status_update = forms.ChoiceField(
        label="定时功能状态",
        choices=timing_status_update_choices,
        initial="0",
        required=True,
        help_text="定时时间必须为标准的cron风格, 否则会不生效",
        widget=forms.widgets.Select(attrs={"class": "form-control col-lg-7"}),
    )

    timing_cron_update = forms.CharField(
        label="定时任务时间",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7"}),
    )

    timing_function_config_update = forms.CharField(
        label="定时任务功能配置",
        required=False,
        help_text='必须为JSON/YAML格式',
        max_length=16384,
        error_messages={"max_length": "定时任务功能配置最大长度为16384位"},
        widget=forms.widgets.Textarea(
            attrs={
                "class": "form-control col-lg-7 hidden-scrollbar-textarea equal-width-font",
                "placeholder": "定时任务功能配置",
                "style": "height: 120px; border-radius: 1rem;",
            }
        ),
    )

    def clean_timing_function_config_update(self):
        field = json_and_yaml_verification(self, "timing_function_config_update")
        return field
