def field_convert_to_icontains(forms, icontains_fileds):
    tmp_data = {}
    for field_name in icontains_fileds:
        field_value = forms.cleaned_data.get(field_name)
        if field_value:
            tmp_data[f"{field_name}__icontains"] = field_value
    return tmp_data


def strint_convert_to_list(forms, list_str_fields):
    list_data = {}
    for field_name in list_str_fields:
        field_str = forms.cleaned_data.get(field_name).strip(" |")
        if field_str:
            field_data_list = [int(i) for i in field_str.split("|")]
        else:
            field_data_list = []
        list_data[field_name] = field_data_list
    return list_data


def get_update_form_html(form_field, align_top_field=[], multi_select_fields=[]):
    # 根据update_form字段属性生成html代码
    
    tooltip = ""
    notice_icon = ""
    is_align_top = ""
    field_html = form_field

    # 给某些标签添加注释
    if form_field.help_text:
        tooltip = f"""data-toggle="tooltip" data-placement="left" title='{form_field.help_text}'"""
        notice_icon = '<i class="fa-solid fa-circle-exclamation text-blue"></i>'

    # 顶部对齐
    if form_field.name in align_top_field:
        is_align_top = "align-self-start"

    # 渲染多选框
    if form_field.name in multi_select_fields:
        field_ele = []
        for radio in form_field:
            field_ele.append(
                f"""
            <span class="custom-control custom-switch">
                {radio.tag()}
                <label for="{radio.id_for_label}" class="custom-control-label mb-0">{radio.choice_label}</label>
            </span>
            """
            )
        field_html = '<div class="col-lg-7 d-flex align-items-center pl-1">{}</div>'.format("<span class='pl-3 pr-3'>-</span>".join(field_ele))

    # 渲染html页面
    html = """
    <div class="form-group row d-flex align-items-center mt-2">
        <div class="col-lg-3 update-modal-label {is_align_top}">
            <label class="mb-1" for="{id}" {tooltip}>
                <span class="text-muted pl-2">{notice_icon} {label} : </span>
            </label>
        </div>
        {field_html}
    </div>
    """.format(
        id=form_field.auto_id,
        tooltip=tooltip,
        is_align_top=is_align_top,
        label=form_field.label,
        notice_icon=notice_icon,
        field_html=field_html,
    )

    return html
