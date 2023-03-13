from django import forms


class ComponentForm(forms.Form):
    component_id = forms.CharField(
        label="组件ID",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    component_role_choices = (("", ""), ("1", "Messenger"), ("2", "Processor"))
    component_role = forms.ChoiceField(
        label="组件角色",
        choices=component_role_choices,
        initial="",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    component_ip = forms.CharField(
        label="组件IP",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    component_status_choices = (("", ""), ("0", "离线中"), ("1", "运行中"))
    component_status = forms.ChoiceField(
        label="组件状态",
        choices=component_status_choices,
        initial="",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
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
