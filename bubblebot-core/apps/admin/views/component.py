import re
from loguru import logger
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..lib.pagination import Pagination
from ..myforms.componentForm import ComponentForm
from robot.models import Components

errors_info = {0: "请求成功", 1: "请求数据错误", 255: "系统繁忙"}

strim_tail_query_repl = re.compile("_query$")


@login_required
def component(request):
    query_forms = ComponentForm()
    return render(request, 'manage/component.html', locals())


# 当做函数用，定义类仅用于做分类
class ComponentApi:
    @login_required
    def query(request):
        errcode = None
        data = {}
        res_json = {}

        try:
            forms = ComponentForm(request.GET)
            if errcode == None:
                if (request.method != 'GET') or (not request.is_ajax):
                    errcode = 255

            # 校验请求的数据
            if errcode == None:
                if not forms.is_valid():
                    data = forms.errors
                    errcode = 1

            # 获取请求的数据
            if errcode == None:
                # 获取所有component数据
                forms.cleaned_data = {re.sub(strim_tail_query_repl, "", k): v for k, v in forms.cleaned_data.items()}

                # 生成过滤数据
                filter_conditions = {}
                component_id = forms.cleaned_data.get("component_id")
                if component_id:
                    filter_conditions["component_id"] = component_id

                component_ip = forms.cleaned_data.get("component_ip")
                if component_ip:
                    filter_conditions["component_ip"] = component_ip

                component_role = forms.cleaned_data.get("component_role")
                if component_role in ("0", "1"):
                    component_role = int(component_role)
                    filter_conditions["component_role"] = component_role

                component_status = forms.cleaned_data.get("component_status")
                if component_status in ("0", "1"):
                    component_status = int(component_status)
                    filter_conditions["component_status"] = component_status

                filtered_data = Components.objects.filter(**filter_conditions).order_by("-create_time")

                # 生成分页数据
                page_index = int(forms.cleaned_data.get("page_index"))
                page_index = page_index if page_index >= 1 else 1
                per_page_num = int(forms.cleaned_data.get("per_page_num"))

                pager = Pagination(filtered_data, page_index, per_page_num)
                current_page_data = []
                for data in pager.current_page_data_list:
                    tmp_data = {}
                    tmp_data["component_id"] = data.component_id
                    tmp_data["component_role"] = data.get_component_role_display()
                    tmp_data["component_ip"] = data.component_ip
                    tmp_data["component_status"] = (
                        "<span class='dot bg-green d-inline-block mr-2'></span>运行中" if data.component_status else "<span class='dot bg-red d-inline-block mr-2'></span>离线中"
                    )
                    tmp_data["last_report_time"] = data.last_report_time.strftime("%Y-%m-%d %H:%M:%S") if data.last_report_time else "-"
                    tmp_data["create_time"] = data.create_time.strftime("%Y-%m-%d %H:%M:%S") if data.create_time else "-"
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
            logger.error(f"查询用户登录记录时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})
