import re
import yaml
from loguru import logger
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..myforms.timingFunctionForm import TimingFunctionQueryForm
from ..myforms.timingFunctionForm import TimingFunctionInsertForm
from ..myforms.timingFunctionForm import TimingFunctionUpdateForm
from ..lib.pagination import Pagination
from ..lib.render import get_update_form_html, field_convert_to_icontains
from robot.models import TimingFunctions


errors_info = {
    0: "成功",
    1: "请求数据错误",
    2: "请传入至少一条要删除的数据",
    3: "添加失败, 该BOT已添加过该定时任务",
    4: "定时功能ID不存在",
    5: "定时功能原ID不存在",
    6: "要更新的定时功能ID已存在",
    7: "更新失败",
    8: "删除失败",
    9: "创建失败",
    255: "系统繁忙",
}

strim_tail_query_repl = re.compile("_query$")


@login_required
def timing_function(request):
    query_forms = TimingFunctionQueryForm()
    insert_forms = TimingFunctionInsertForm()
    return render(request, 'manage/timing_function.html', locals())


class TimingFunctionApi:
    # ============================================================================================
    @login_required
    def query(request):
        errcode = None
        data = {}
        res_json = {}
        try:
            forms = TimingFunctionQueryForm(request.GET)
            if errcode == None:
                if (request.method != 'GET') or (not request.is_ajax):
                    errcode = 255

            # 校验请求的数据
            if errcode == None:
                if not forms.is_valid():
                    errcode = 1

            # 获取请求的数据
            if errcode == None:
                # 获取所有timing function数据
                forms.cleaned_data = {re.sub(strim_tail_query_repl, "", k): v for k, v in forms.cleaned_data.items()}

                # 生成过滤数据
                filter_conditions = {}
                timing_function_id = forms.cleaned_data.get("timing_function_id")
                if timing_function_id:
                    filter_conditions["timing_function_id"] = timing_function_id

                timing_function_class = forms.cleaned_data.get("timing_function_class")
                if timing_function_class:
                    filter_conditions["timing_function_class"] = timing_function_class

                global_function_status = forms.cleaned_data.get("global_function_status")
                if global_function_status in ("0", "1"):
                    global_function_status = int(global_function_status)
                    filter_conditions["global_function_status"] = global_function_status

                icontains_fileds = ['timing_function_name' 'explain']
                filter_conditions.update(field_convert_to_icontains(forms, icontains_fileds))
                filtered_data = TimingFunctions.objects.filter(**filter_conditions).order_by("-create_time")

                # 生成分页数据
                page_index = int(forms.cleaned_data.get("page_index"))
                page_index = page_index if page_index >= 1 else 1
                per_page_num = int(forms.cleaned_data.get("per_page_num"))

                pager = Pagination(filtered_data, page_index, per_page_num)
                current_page_data = []
                for data in pager.current_page_data_list:
                    tmp_data = {}
                    tmp_data["timing_function_id"] = data.timing_function_id
                    tmp_data["timing_function_name"] = data.timing_function_name
                    tmp_data["timing_function_url"] = data.timing_function_url
                    tmp_data["timing_function_class"] = data.timing_function_class if data.timing_function_class else "-"
                    tmp_data["default_timing_cron"] = data.default_timing_cron if data.default_timing_cron else "-"
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
            logger.error(f"查询TIMING FUNCTION记录时出错: {repr(e)}")
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
            forms = TimingFunctionInsertForm(request.POST)
            if errcode == None:
                if (request.method != 'POST') or (not request.is_ajax):
                    errcode = 255

            if errcode == None:
                if not forms.is_valid():
                    errcode = 1
                    data = forms.errors

            if errcode == None:
                # 查询提交的function_id, 如果存在则返回错误信息, 如果不存在则创建
                timing_function_id = forms.cleaned_data.get("timing_function_id_insert")
                timing_function_obj = TimingFunctions.objects.filter(timing_function_id=timing_function_id)
                if timing_function_obj:
                    errcode = 3

            if errcode == None:
                # 处理数据
                default_function_config = yaml.safe_load(forms.cleaned_data.get("default_function_config_insert"))
                if not isinstance(default_function_config, (dict, list)):
                    default_function_config = {}

                function_data = {
                    'timing_function_id': timing_function_id,
                    'timing_function_name': forms.cleaned_data.get("timing_function_name_insert"),
                    'timing_function_url': forms.cleaned_data.get("timing_function_url_insert"),
                    'timing_function_class': forms.cleaned_data.get("timing_function_class_insert"),
                    'global_function_status': forms.cleaned_data.get("global_function_status_insert"),
                    'default_timing_cron': forms.cleaned_data.get("default_timing_cron_insert"),
                    'default_function_config': default_function_config,
                    'explain': forms.cleaned_data.get("explain_insert"),
                }
                res = TimingFunctions.objects.create(**function_data)
                if res:
                    logger.info(f"用户 [{request.user}] 执行添加功能 [{timing_function_id}] 成功!")
                    errcode = 0
                else:
                    logger.info(f"用户 [{request.user}] 执行添加功能 [{timing_function_id}] 失败!")
                    errcode = 9

        except Exception as e:
            errcode = 255
            logger.error(f"添加TIMING FUNCTION记录时出错: {repr(e)}")
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
                print(delete_id_list)
                timing_functions_obj = TimingFunctions.objects.filter(timing_function_id__in=delete_id_list)
                if timing_functions_obj.count() != len(delete_id_list):
                    errcode = 4

            if errcode == None:
                # 如果正常则删除对应数据
                res = timing_functions_obj.delete()
                if res[0] > 0:
                    logger.info(f"用户 [{request.user}] 执行删除功能 {delete_id_list} 成功!")
                    errcode = 0
                else:
                    logger.info(f"用户 [{request.user}] 执行删除功能 {delete_id_list} 失败!")
                    errcode = 8

        except Exception as e:
            errcode = 255
            logger.error(f"删除TIMING FUNCTION记录时出错: {repr(e)}")
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
                    timing_function_id = request.GET.get("id")
                    timing_function_obj = TimingFunctions.objects.filter(timing_function_id=timing_function_id)

                    # 如果没有这个function, 则返回错误
                    if errcode == None:
                        if not timing_function_obj:
                            errcode = 4

                    if errcode == None:
                        timing_function_data = timing_function_obj.first()

                        if timing_function_data.default_function_config:
                            default_function_config_update = timing_function_data.default_function_config
                        else:
                            default_function_config_update = ""

                        form_initial_data = {
                            'timing_function_id_update': timing_function_data.timing_function_id,
                            'timing_function_name_update': timing_function_data.timing_function_name,
                            'timing_function_url_update': timing_function_data.timing_function_url,
                            'timing_function_class_update': timing_function_data.timing_function_class,
                            'global_function_status_update': timing_function_data.global_function_status,
                            'default_timing_cron_update': timing_function_data.default_timing_cron,
                            'default_function_config_update': yaml.safe_dump(default_function_config_update, allow_unicode=True, default_flow_style=False, sort_keys=False),
                            'explain_update': timing_function_data.explain,
                        }

                        # 获取渲染后的HTML
                        html_list = [f'<form id="updateForm" original-timing-function-id="{timing_function_data.timing_function_id}">']
                        forms = TimingFunctionUpdateForm(initial=form_initial_data)
                        for form_field in forms:
                            html_list.append(get_update_form_html(form_field, align_top_field=("default_function_config_update", "explain_update")))
                        else:
                            html_list.append("</form>")

                        data = {"html": "\n".join(html_list)}
                        errcode = 0

        except Exception as e:
            errcode = 255
            logger.error(f"查询TIMING FUNCTION配置时出错: {repr(e)}")
            logger.exception(e)

        # POST请求
        try:
            # ==========================================================================================================
            if request.method == 'POST':
                forms = TimingFunctionUpdateForm(request.POST)

                if errcode == None:
                    if not forms.is_valid():
                        errcode = 1
                        data = forms.errors

                # 判断是否存在该function
                if errcode == None:
                    original_timing_function_id = request.POST.get("original_timing_function_id")
                    original_timing_function_obj = TimingFunctions.objects.filter(timing_function_id=original_timing_function_id)
                    if not original_timing_function_obj:
                        errcode = 5

                # 如果要修改function_id, 则判断目标function_id是否已存在
                if errcode == None:
                    update_timing_function_id = forms.cleaned_data.get("timing_function_id_update")
                    if update_timing_function_id != original_timing_function_id:
                        update_timing_function_obj = TimingFunctions.objects.filter(timing_function_id=update_timing_function_id)
                        if update_timing_function_obj:
                            errcode = 6

                if errcode == None:
                    # 获取数据

                    default_function_config = yaml.safe_load(forms.cleaned_data.get("default_function_config_update"))
                    if not isinstance(default_function_config, (dict, list)):
                        default_function_config = {}

                    new_data = {
                        'timing_function_id': update_timing_function_id,
                        'timing_function_name': forms.cleaned_data.get("timing_function_name_update"),
                        'timing_function_url': forms.cleaned_data.get("timing_function_url_update"),
                        'timing_function_class': forms.cleaned_data.get("timing_function_class_update"),
                        'global_function_status': int(forms.cleaned_data.get("global_function_status_update")),
                        'default_timing_cron': forms.cleaned_data.get("default_timing_cron_update"),
                        'default_function_config': default_function_config,
                        'explain': forms.cleaned_data.get("explain_update"),
                    }

                    res = original_timing_function_obj.update(**new_data)
                    if res:
                        logger.info(f"用户 [{request.user}] 更新功能配置成功! [{original_timing_function_id}] => {new_data}")
                        errcode = 0
                    else:
                        logger.info(f"用户 [{request.user}] 更新功能配置失败! [{original_timing_function_id}] => {new_data}")
                        errcode = 7

        except Exception as e:
            errcode = 255
            logger.error(f"更新TIMING FUNCTION配置时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})
