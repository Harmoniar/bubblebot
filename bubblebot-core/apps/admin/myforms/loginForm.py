from django import forms


class LoginForm(forms.Form):
    useremail = forms.EmailField(
        max_length=120,
        required=True,
        widget=forms.widgets.TextInput(attrs={"placeholder": "User Email", "class": "form-control border-0 shadow form-control-lg"}),
        error_messages={"required": "用户名不能为空"},
    )

    password = forms.CharField(
        required=True,
        widget=forms.widgets.TextInput(attrs={"type": "password", "placeholder": "Password", "class": "form-control border-0 shadow form-control-lg text-violet"}),
        error_messages={"required": "密码不能为空"},
    )
