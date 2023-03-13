from django import forms


class LoginLogQueryForm(forms.Form):
    login_ip = forms.CharField(
        label="登录IP",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    login_location = forms.CharField(
        label="登录位置",
        required=False,
        widget=forms.widgets.TextInput(attrs={"class": "form-control"}),
    )

    login_result_choices = (("", ""), ("0", "成功"), ("1", "失败"))
    login_result = forms.ChoiceField(
        label="登录结果",
        choices=login_result_choices,
        initial="",
        required=False,
        widget=forms.widgets.Select(attrs={"class": "form-control"}),
    )

    start_date = forms.DateField(
        label="起始时间",
        required=False,
        widget=forms.widgets.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    end_date = forms.DateField(
        label="结束时间",
        required=False,
        widget=forms.widgets.DateInput(attrs={"type": "date", "class": "form-control"}),
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
