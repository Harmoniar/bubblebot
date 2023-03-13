from django import forms
from ..lib.verification import json_and_yaml_verification


class TimingFunctionQueryForm(forms.Form):
    timing_function_id_query = forms.CharField(
        label="功能ID",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    timing_function_name_query = forms.CharField(
        label="定时功能名称",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    timing_function_url_query = forms.CharField(
        label="定时功能路径",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    timing_function_class_query = forms.CharField(
        label="定时功能分类",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    global_function_status_query_choices = (("", ""), ("0", "停用"), ("1", "启用"))
    global_function_status_query = forms.ChoiceField(
        label="功能状态",
        choices=global_function_status_query_choices,
        initial="",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
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


class TimingFunctionInsertForm(forms.Form):

    timing_function_id_insert = forms.CharField(
        label="功能ID",
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "功能ID"}),
    )

    timing_function_name_insert = forms.CharField(
        label="功能名称",
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "功能名称"}),
    )

    timing_function_url_insert = forms.CharField(
        label="功能路径",
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "功能路径"}),
    )

    timing_function_class_insert = forms.CharField(
        label="功能分类",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "功能分类"}),
    )

    global_function_status_insert_choices = (("0", "停用"), ("1", "启用"))
    global_function_status_insert = forms.ChoiceField(
        label="功能状态",
        choices=global_function_status_insert_choices,
        initial="0",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    default_timing_cron_insert = forms.CharField(
        label="默认定时时间",
        required=False,
        max_length=255,
        widget=forms.widgets.TextInput(attrs={"class": "form-control", "placeholder": "功能分类"}),
        error_messages={"max_length": "定时时间最大长度为255位"},
    )

    default_function_config_insert = forms.CharField(
        label="默认定时功能配置",
        required=False,
        help_text='必须为JSON/YAML格式',
        max_length=16384,
        error_messages={"max_length": "默认触发命令参数最大长度为16384位"},
        widget=forms.widgets.Textarea(
            attrs={"class": "form-control hidden-scrollbar-textarea equal-width-font", "placeholder": "默认触发命令的参数", "style": "height: 120px; border-radius: 1rem;"}
        ),
    )

    explain_insert = forms.CharField(
        label="定时功能说明",
        required=False,
        max_length=2048,
        error_messages={"max_length": "功能说明最大长度为2048位"},
        widget=forms.widgets.Textarea(
            attrs={"class": "form-control hidden-scrollbar-textarea equal-width-font", "placeholder": "功能说明", "style": "height: 120px; border-radius: 1rem;"}
        ),
    )

    def clean_default_function_config_insert(self):
        field = json_and_yaml_verification(self, "default_function_config_insert")
        return field


class TimingFunctionUpdateForm(forms.Form):

    timing_function_id_update = forms.CharField(
        label="功能ID",
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "功能ID"}),
    )

    timing_function_name_update = forms.CharField(
        label="功能名称",
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "功能名称"}),
    )

    timing_function_url_update = forms.CharField(
        label="功能路径",
        required=True,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "功能路径"}),
    )

    timing_function_class_update = forms.CharField(
        label="功能分类",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "功能分类"}),
    )

    global_function_status_update_choices = (("0", "停用"), ("1", "启用"))
    global_function_status_update = forms.ChoiceField(
        label="功能状态",
        choices=global_function_status_update_choices,
        initial="0",
        required=True,
        widget=forms.widgets.Select(attrs={"class": "form-control col-lg-7"}),
    )

    default_timing_cron_update = forms.CharField(
        label="默认定时时间",
        required=False,
        help_text="定时时间必须为标准的cron风格, 否则会不生效",
        max_length=255,
        widget=forms.widgets.TextInput(attrs={"class": "form-control col-lg-7", "placeholder": "功能分类"}),
        error_messages={"max_length": "定时时间最大长度为255位"},
    )

    default_function_config_update = forms.CharField(
        label="默认定时功能配置",
        required=False,
        help_text='必须为JSON/YAML格式',
        max_length=16384,
        error_messages={"max_length": "默认触发命令参数最大长度为16384位"},
        widget=forms.widgets.Textarea(
            attrs={"class": "form-control col-lg-7 hidden-scrollbar-textarea equal-width-font", "placeholder": "默认触发命令的参数", "style": "height: 120px; border-radius: 1rem;"}
        ),
    )

    explain_update = forms.CharField(
        label="定时功能说明",
        required=False,
        max_length=2048,
        error_messages={"max_length": "功能说明最大长度为2048位"},
        widget=forms.widgets.Textarea(
            attrs={"class": "form-control col-lg-7 hidden-scrollbar-textarea equal-width-font", "placeholder": "功能说明", "style": "height: 120px; border-radius: 1rem;"}
        ),
    )

    def clean_default_function_config_update(self):
        field = json_and_yaml_verification(self, "default_function_config_update")
        return field
