import datetime
from loguru import logger
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..lib.pagination import Pagination
from ..myforms.loginlogForm import LoginLogQueryForm
from ..models import UserLoginLog


errors_info = {0: "请求成功", 1: "请求数据错误", 255: "系统繁忙"}


@login_required
def loginlog(request):
    query_forms = LoginLogQueryForm()
    return render(request, 'manage/loginlog.html', locals())


# 当做函数用，定义类仅用于做分类
class LoginLogApi:
    @login_required
    def query(request):
        errcode = None
        data = {}
        res_json = {}

        try:
            if errcode == None:
                if (request.method != 'GET') or (not request.is_ajax):
                    errcode = 255

            # 校验请求的数据
            if errcode == None:
                forms = LoginLogQueryForm(request.GET)
                if not forms.is_valid():
                    data = forms.errors
                    errcode = 1

            # 获取请求的数据
            if errcode == None:
                filter_conditions = {}
                filter_conditions["login_user"] = request.user

                base_filter = ['login_ip', 'login_result']
                for field_name in base_filter:
                    field_value = forms.cleaned_data.get(field_name)
                    if field_value:
                        filter_conditions[field_name] = field_value

                login_location = forms.cleaned_data.get("login_location")
                if login_location:
                    filter_conditions["login_location__icontains"] = login_location

                start_date = forms.cleaned_data.get("start_date")
                if start_date:
                    filter_conditions["login_time__gte"] = start_date

                end_date = forms.cleaned_data.get("end_date")
                if start_date:
                    end_date = datetime.datetime.strptime("{} 23:59:59".format(end_date), "%Y-%m-%d %H:%M:%S")
                    filter_conditions["login_time__lte"] = end_date

                page_index = int(forms.cleaned_data.get("page_index"))
                page_index = page_index if page_index >= 1 else 1
                per_page_num = int(forms.cleaned_data.get("per_page_num"))

                queryset = UserLoginLog.objects.filter(**filter_conditions).order_by("-id")

                pager = Pagination(queryset, page_index, per_page_num)
                current_page_data = []
                for queryset in pager.current_page_data_list:
                    tmp_data = {}
                    tmp_data["login_ip"] = queryset.login_ip
                    tmp_data["login_location"] = queryset.login_location
                    tmp_data["login_time"] = queryset.login_time.strftime("%Y-%m-%d %H:%M:%S")
                    tmp_data["login_result"] = queryset.get_login_result_display()
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
