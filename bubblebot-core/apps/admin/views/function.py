import re
import yaml
from loguru import logger
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..myforms.functionForm import FunctionQueryForm
from ..myforms.functionForm import FunctionInsertForm
from ..myforms.functionForm import FunctionUpdateForm
from ..lib.pagination import Pagination
from ..lib.render import get_update_form_html, field_convert_to_icontains
from robot.models import Functions


errors_info = {0: "成功", 1: "请求数据错误", 2: "请传入至少一条要删除的数据", 3: "添加失败, 功能ID已存在", 4: "功能ID不存在", 5: "功能原ID不存在", 6: "要更新的功能ID已存在", 7: "更新失败", 8: "删除失败", 9: "创建失败", 255: "系统繁忙"}

strim_tail_query_repl = re.compile("_query$")


@login_required
def function(request):
    query_forms = FunctionQueryForm()
    insert_forms = FunctionInsertForm()
    return render(request, 'manage/function.html', locals())


class FunctionApi:
    # ============================================================================================
    @login_required
    def query(request):
        errcode = None
        data = {}
        res_json = {}
        try:
            forms = FunctionQueryForm(request.GET)
            if errcode == None:
                if (request.method != 'GET') or (not request.is_ajax):
                    errcode = 255

            # 校验请求的数据
            if errcode == None:
                if not forms.is_valid():
                    errcode = 1

            # 获取请求的数据
            if errcode == None:
                # 获取所有function数据
                forms.cleaned_data = {re.sub(strim_tail_query_repl, "", k): v for k, v in forms.cleaned_data.items()}

                # 生成过滤数据
                filter_conditions = {}
                function_id = forms.cleaned_data.get("function_id")
                if function_id:
                    filter_conditions["function_id"] = function_id

                function_class = forms.cleaned_data.get("function_class")
                if function_class:
                    filter_conditions["function_class"] = function_class

                global_function_status = forms.cleaned_data.get("global_function_status")
                if global_function_status in ("0", "1"):
                    global_function_status = int(global_function_status)
                    filter_conditions["global_function_status"] = global_function_status

                icontains_fileds = ['function_name', 'function_url', 'explain', 'default_trigger_command']
                filter_conditions.update(field_convert_to_icontains(forms, icontains_fileds))

                filtered_data = Functions.objects.filter(**filter_conditions).order_by("-create_time")

                # 生成分页数据
                page_index = int(forms.cleaned_data.get("page_index"))
                page_index = page_index if page_index >= 1 else 1
                per_page_num = int(forms.cleaned_data.get("per_page_num"))

                pager = Pagination(filtered_data, page_index, per_page_num)
                current_page_data = []
                for data in pager.current_page_data_list:
                    tmp_data = {}
                    tmp_data["function_id"] = data.function_id
                    tmp_data["function_name"] = data.function_name
                    tmp_data["function_url"] = data.function_url
                    tmp_data["function_class"] = data.function_class if data.function_class else "-"
                    tmp_data["global_function_status"] = (
                        "<span class='dot bg-green d-inline-block mr-2'></span>已启用" if data.global_function_status else "<span class='dot bg-red d-inline-block mr-2'></span>已停用"
                    )
                    tmp_data["explain"] = data.explain if data.explain else "-"
                    current_page_data.append(tmp_data)

                data = {
                    "total_row_num": pager.total_row_num,
                    "total_page_num": pager.total_page_num,
                    "total_page_range": pager.total_page_range,
                    "current_row_range": pager.current_row_range,
                    "current_page_num": pager.current_page_num,
                    "has_next": pager.has_next,
                    "has_previous": pager.has_previous,
                    "current_page_data": current_page_data,
                }
                errcode = 0

        except Exception as e:
            errcode = 255
            logger.error(f"查询FUNCTION记录时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})

    # ============================================================================================
    @login_required
    def insert(request):
        errcode = None
        data = {}
        res_json = {}

        try:
            forms = FunctionInsertForm(request.POST)
            if errcode == None:
                if (request.method != 'POST') or (not request.is_ajax):
                    errcode = 255

            if errcode == None:
                if not forms.is_valid():
                    errcode = 1
                    data = forms.errors

            if errcode == None:
                # 查询提交的function_id, 如果存在则返回错误信息, 如果不存在则创建
                function_id = forms.cleaned_data.get("function_id_insert")
                function_obj = Functions.objects.filter(function_id=function_id)
                if function_obj:
                    errcode = 3

            if errcode == None:
                # 处理数据
                default_trigger_command_str = forms.cleaned_data.get("default_trigger_command_insert").strip(" ,|")
                if default_trigger_command_str:
                    default_trigger_command_list = [i.strip() for i in default_trigger_command_str.split("|")]
                else:
                    default_trigger_command_list = []

                default_command_args = yaml.safe_load(forms.cleaned_data.get("default_command_args_insert"))
                if not isinstance(default_command_args, (dict, list)):
                    default_command_args = []

                default_trigger_template = yaml.safe_load(forms.cleaned_data.get("default_trigger_template_insert"))
                if not isinstance(default_trigger_template, (dict, list)):
                    default_trigger_template = {}

                default_exception_template = yaml.safe_load(forms.cleaned_data.get("default_exception_template_insert"))
                if not isinstance(default_exception_template, (dict, list)):
                    default_exception_template = {}

                function_data = {
                    'function_id': function_id,
                    'function_name': forms.cleaned_data.get("function_name_insert"),
                    'function_url': forms.cleaned_data.get("function_url_insert"),
                    'function_class': forms.cleaned_data.get("function_class_insert"),
                    'global_function_status': forms.cleaned_data.get("global_function_status_insert"),
                    'default_trigger_command': default_trigger_command_list,
                    'default_command_args': default_command_args,
                    'default_trigger_template': default_trigger_template,
                    'default_exception_template': default_exception_template,
                    'explain': forms.cleaned_data.get("explain_insert"),
                }
                res = Functions.objects.create(**function_data)
                if res:
                    logger.info(f"用户 [{request.user}] 执行添加功能 [{function_id}] 成功!")
                    errcode = 0
                else:
                    logger.info(f"用户 [{request.user}] 执行添加功能 [{function_id}] 失败!")
                    errcode = 9

        except Exception as e:
            errcode = 255
            logger.error(f"添加FUNCTION记录时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})

    # ============================================================================================
    @login_required
    def delete(request):
        errcode = None
        data = {}
        res_json = {}
        try:
            if errcode == None:
                if (request.method != 'POST') or (not request.is_ajax):
                    errcode = 255

            if errcode == None:
                delete_id_list = request.POST.getlist("data_id_list")
                if len(delete_id_list) < 1:
                    errcode = 2

            if errcode == None:
                # 查询出所有的符合条件的function，如果数量和delete_id_list的数量对不上，则返回错误
                functions_obj = Functions.objects.filter(function_id__in=delete_id_list)
                if functions_obj.count() != len(delete_id_list):
                    errcode = 4

            if errcode == None:
                # 如果正常则删除对应数据
                res = functions_obj.delete()
                if res[0] > 0:
                    logger.info(f"用户 [{request.user}] 执行删除功能 {delete_id_list} 成功!")
                    errcode = 0
                else:
                    logger.info(f"用户 [{request.user}] 执行删除功能 {delete_id_list} 失败!")
                    errcode = 8

        except Exception as e:
            errcode = 255
            logger.error(f"删除FUNCTION记录时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})

    # ============================================================================================
    @login_required
    def update(request):
        errcode = None
        data = {}
        res_json = {}

        if errcode == None:
            if (request.method not in ('GET', 'POST')) or (not request.is_ajax):
                errcode = 255

        # GET请求
        try:
            if errcode == None:
                # 获取模态框需要的数据
                if request.method == 'GET':
                    function_id = request.GET.get("id")
                    function_obj = Functions.objects.filter(function_id=function_id)

                    # 如果没有这个function, 则返回错误
                    if errcode == None:
                        if not function_obj:
                            errcode = 4

                    if errcode == None:
                        function_data = function_obj.first()
                        form_initial_data = {
                            'function_id_update': function_data.function_id,
                            'function_name_update': function_data.function_name,
                            'function_url_update': function_data.function_url,
                            'function_class_update': function_data.function_class,
                            'global_function_status_update': function_data.global_function_status,
                            'default_trigger_command_update': " | ".join(function_data.default_trigger_command),
                            'default_command_args_update': yaml.safe_dump(function_data.default_command_args, allow_unicode=True, default_flow_style=False, sort_keys=False)
                            if function_data.default_command_args
                            else "",
                            'default_trigger_template_update': yaml.safe_dump(function_data.default_trigger_template, allow_unicode=True, default_flow_style=False, sort_keys=False)
                            if function_data.default_trigger_template
                            else "",
                            'default_exception_template_update': yaml.safe_dump(
                                function_data.default_exception_template, allow_unicode=True, default_flow_style=False, sort_keys=False
                            )
                            if function_data.default_exception_template
                            else "",
                            'explain_update': function_data.explain,
                        }

                        # 获取渲染后的HTML
                        html_list = [f'<form id="updateForm" original-function-id="{function_data.function_id}">']
                        forms = FunctionUpdateForm(initial=form_initial_data)
                        for form_field in forms:
                            html_list.append(
                                get_update_form_html(
                                    form_field, align_top_field=("default_command_args_update", "default_trigger_template_update", "default_exception_template_update")
                                )
                            )
                        else:
                            html_list.append("</form>")

                        data = {"html": "\n".join(html_list)}
                        errcode = 0

        except Exception as e:
            errcode = 255
            logger.error(f"查询FUNCTION配置时出错: {repr(e)}")
            logger.exception(e)

        # POST请求
        try:
            # ==========================================================================================================
            if request.method == 'POST':
                forms = FunctionUpdateForm(request.POST)

                if errcode == None:
                    if not forms.is_valid():
                        errcode = 1
                        data = forms.errors

                # 判断是否存在该function
                if errcode == None:
                    original_function_id = request.POST.get("original_function_id")
                    original_function_obj = Functions.objects.filter(function_id=original_function_id)
                    if not original_function_obj:
                        errcode = 5

                # 如果要修改function_id, 则判断目标function_id是否已存在
                if errcode == None:
                    update_function_id = forms.cleaned_data.get("function_id_update")
                    if update_function_id != original_function_id:
                        update_function_obj = Functions.objects.filter(function_id=update_function_id)
                        if update_function_obj:
                            errcode = 6

                if errcode == None:
                    # 获取数据
                    default_trigger_command_str = forms.cleaned_data.get("default_trigger_command_update").strip(" ,|")
                    if default_trigger_command_str:
                        default_trigger_command_list = [i.strip() for i in default_trigger_command_str.split("|")]
                    else:
                        default_trigger_command_list = []

                    default_command_args = yaml.safe_load(forms.cleaned_data.get("default_command_args_update"))
                    if not isinstance(default_command_args, (dict, list)):
                        default_command_args = []

                    default_trigger_template = yaml.safe_load(forms.cleaned_data.get("default_trigger_template_update"))
                    if not isinstance(default_trigger_template, (dict, list)):
                        default_trigger_template = {}

                    default_exception_template = yaml.safe_load(forms.cleaned_data.get("default_exception_template_update"))
                    if not isinstance(default_exception_template, (dict, list)):
                        default_exception_template = {}

                    new_data = {
                        'function_id': update_function_id,
                        'function_name': forms.cleaned_data.get("function_name_update"),
                        'function_url': forms.cleaned_data.get("function_url_update"),
                        'function_class': forms.cleaned_data.get("function_class_update"),
                        'global_function_status': int(forms.cleaned_data.get("global_function_status_update")),
                        'default_trigger_command': default_trigger_command_list,
                        'default_command_args': default_command_args,
                        'default_trigger_template': default_trigger_template,
                        'default_exception_template': default_exception_template,
                        'explain': forms.cleaned_data.get("explain_update"),
                    }

                    res = original_function_obj.update(**new_data)
                    if res:
                        logger.info(f"用户 [{request.user}] 更新功能配置成功! [{original_function_id}] => {new_data}")
                        errcode = 0
                    else:
                        logger.info(f"用户 [{request.user}] 更新功能配置失败! [{original_function_id}] => {new_data}")
                        errcode = 7

        except Exception as e:
            errcode = 255
            logger.error(f"更新FUNCTION配置时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})
