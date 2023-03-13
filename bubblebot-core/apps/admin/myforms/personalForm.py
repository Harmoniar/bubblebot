from django import forms


class ModifyPersonalInfoForm(forms.Form):
    avatar = forms.ImageField(label='User Avatar', required=False, widget=forms.widgets.FileInput(attrs={"class": "avatar_file_input"}))

    username = forms.CharField(
        label='User Name',
        max_length=32,
        error_messages={"required": "用户名不能为空", "max_length": "用户名不能大于32位"},
        widget=forms.widgets.TextInput(attrs={"class": "form-control pl-3", "placeholder": "用户名"}),
    )

    old_password = forms.CharField(
        label='Old Password',
        required=False,
        widget=forms.widgets.PasswordInput(attrs={"class": "form-control pl-3", "placeholder": "原密码"}),
    )

    new_password = forms.CharField(
        label='New Password',
        required=False,
        min_length=8,
        max_length=48,
        error_messages={"min_length": "新密码不能小于8位", "max_length": "新密码不能大于48位"},
        widget=forms.widgets.PasswordInput(attrs={"class": "form-control pl-3", "placeholder": "新密码"}),
    )

    # 如果写了新密码，则判断原密码是否为空
    def clean(self):
        old_password = self.cleaned_data.get("old_password")
        new_password = self.cleaned_data.get("new_password")
        if new_password and (not old_password):
            self.add_error("old_password", "如果要修改密码，则原密码不能为空")

        return self.cleaned_data
