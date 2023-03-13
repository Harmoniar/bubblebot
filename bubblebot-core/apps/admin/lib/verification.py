import yaml


def json_and_yaml_verification(forms, field_name):
    field_data = forms.cleaned_data.get(field_name)
    if field_data:
        format_error = "服务器配置的JSON/YAML格式错误, 请检查后重试"
        try:
            yaml_obj = yaml.safe_load(field_data)
            if not isinstance(yaml_obj, (dict, list)):
                forms.add_error(field_name, format_error)
        except Exception:
            forms.add_error(field_name, format_error)
    return field_data
