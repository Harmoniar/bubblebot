import re
import yaml
from loguru import logger
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from ..myforms.robotTimingForm import RobotTimingQueryForm
from ..myforms.robotTimingForm import RobotTimingInsertForm
from ..myforms.robotTimingForm import RobotTimingUpdateForm
from ..lib.pagination import Pagination
from ..lib.render import get_update_form_html, field_convert_to_icontains
from robot.models import Robots
from robot.models import TimingFunctions
from robot.models import Robot2Timing


errors_info = {
    0: "成功",
    1: "请求数据错误",
    2: "请传入至少一条要删除的数据",
    3: "添加失败, 定时功能ID已存在",
    4: "定时功能ID不存在",
    5: "定时功能原ID不存在",
    6: "要更新的定时功能ID已存在",
    7: "更新失败",
    8: "删除失败",
    9: "机器人ID不存在",
    255: "系统繁忙",
}

strim_tail_query_repl = re.compile("_query$")


@login_required
def robot_timing(request):
    # 获取用户所有机器人ID, 和现存所有已启用的功能ID
    user_robots = [(i.get("robot_id"), i.get("robot_id")) for i in Robots.objects.filter(admin_user=request.user).values("robot_id")]
    all_functions = [
        (i.get("timing_function_id"), i.get("timing_function_name"))
        for i in TimingFunctions.objects.filter(global_function_status=1).values("timing_function_id", "timing_function_name")
    ]

    query_user_robots = [("", "")]
    query_user_robots.extend(user_robots)
    query_all_timing_functions = [("", "")]
    query_all_timing_functions.extend(all_functions)

    query_forms = []
    for field in RobotTimingQueryForm():
        if field.name == "robot_id_query":
            field.field.widget.choices = query_user_robots

        elif field.name == "timing_function_id_query":
            field.field.widget.choices = query_all_timing_functions
        query_forms.append(field)

    insert_user_robots = [("", "请选择机器人ID")]
    insert_user_robots.extend(user_robots)
    insert_all_functions = [("", "请选择定时功能")]
    insert_all_functions.extend(all_functions)

    insert_forms = []
    for field in RobotTimingInsertForm():
        if field.name == "robot_id_insert":
            field.field.widget.choices = insert_user_robots
        elif field.name == "timing_function_id_insert":
            field.field.widget.choices = insert_all_functions
        insert_forms.append(field)

    return render(request, 'main/robot_timing.html', locals())


class RobotTimingApi:
    # ============================================================================================
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
                forms = RobotTimingQueryForm(request.GET)
                if not forms.is_valid():
                    errcode = 1
                    data = forms.errors

            # 获取请求的数据
            if errcode == None:
                # 获取用户所有的robot的function数据
                forms.cleaned_data = {re.sub(strim_tail_query_repl, "", k): v for k, v in forms.cleaned_data.items()}

                # 生成过滤数据
                filter_conditions = {}
                robot_id = forms.cleaned_data.get("robot_id")
                if robot_id:
                    filter_conditions["robot_id"] = robot_id

                function_id = forms.cleaned_data.get("timing_function_name")
                if function_id:
                    filter_conditions["timing_function_id"] = function_id

                timing_status = forms.cleaned_data.get("timing_status")
                if timing_status in ("0", "1"):
                    timing_status = int(timing_status)
                    filter_conditions["timing_status"] = timing_status

                icontains_fileds = ['timing_function.explain']
                filter_conditions.update(field_convert_to_icontains(forms, icontains_fileds))

                filtered_data = Robot2Timing.objects.filter(**filter_conditions).order_by("id")

                # 生成分页数据
                page_index = int(forms.cleaned_data.get("page_index"))
                page_index = page_index if page_index >= 1 else 1
                per_page_num = int(forms.cleaned_data.get("per_page_num"))

                pager = Pagination(filtered_data, page_index, per_page_num)
                current_page_data = []
                for data in pager.current_page_data_list:
                    if data.timing_function.global_function_status:
                        if data.timing_status:
                            timing_status_html = "<span class='dot bg-green d-inline-block mr-2'></span>已启用"
                        else:
                            timing_status_html = "<span class='dot bg-red d-inline-block mr-2'></span>已禁用"
                    else:
                        timing_status_html = "<span class='dot bg-red d-inline-block mr-2'></span>管理员禁用"

                    tmp_data = {}
                    tmp_data["robot_id"] = data.robot_id
                    tmp_data["timing_function_id"] = data.timing_function_id
                    tmp_data["timing_function_name"] = data.timing_function.timing_function_name
                    tmp_data["timing_cron"] = data.timing_cron
                    tmp_data["timing_status"] = timing_status_html
                    tmp_data["explain"] = data.timing_function.explain if data.timing_function.explain else "-"
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
            logger.error(f"查询ROBOT TIMING记录时出错: {repr(e)}")
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

            if errcode == None:
                if (request.method != 'POST') or (not request.is_ajax):
                    errcode = 255

            if errcode == None:
                forms = RobotTimingInsertForm(request.POST)
                if not forms.is_valid():
                    errcode = 1
                    data = forms.errors

            if errcode == None:
                # 查询用户提交的robot是否存在并属于用户
                robot_id = forms.cleaned_data.get("robot_id_insert")
                robot_obj = Robots.objects.filter(admin_user=request.user, robot_id=robot_id)
                if not robot_obj:
                    errcode = 9

            if errcode == None:
                # 查询用户提交的timing_function是否存在
                timing_function_id = forms.cleaned_data.get("timing_function_id_insert")
                print(timing_function_id)
                timing_function_obj = TimingFunctions.objects.filter(timing_function_id=timing_function_id)
                if not timing_function_obj:
                    errcode = 4

            if errcode == None:
                # 查询用户提交的robot timing_function, 如果存在则返回错误信息, 如果不存在则创建
                robot_timing_function_obj = Robot2Timing.objects.filter(admin_user=request.user, robot_id=robot_id, timing_function_id=timing_function_id)
                if robot_timing_function_obj:
                    errcode = 3

            if errcode == None:
                # 处理并生成数据并用于创建
                timing_function_obj = timing_function_obj.first()
                robot_function_data = {
                    'admin_user_id': str(request.user),
                    'robot_id': robot_id,
                    'timing_function_id': timing_function_id,
                    'timing_status': forms.cleaned_data.get("timing_status_insert"),
                    'timing_cron': timing_function_obj.default_timing_cron,
                    'timing_function_config': timing_function_obj.default_function_config,
                }
                res = Robot2Timing.objects.create(**robot_function_data)
                if res:
                    logger.info(f"用户 [{request.user}] 执行添加机器人功能 [{robot_id}-{timing_function_id}] 成功!")
                    errcode = 0
                else:
                    logger.info(f"用户 [{request.user}] 执行添加机器人功能 [{robot_id}-{timing_function_id}] 失败!")
                    errcode = 9

        except Exception as e:
            errcode = 255
            logger.error(f"添加ROBOT TIMING记录时出错: {repr(e)}")
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
                delete_id_list = [i.split('==:::==') for i in delete_id_list]
                if len(delete_id_list) < 1:
                    errcode = 2

            if errcode == None:
                # 查询出用户所有的符合条件的robot的function，如果数量和delete_id_list的数量对不上，则返回错误
                timing_functions_obj_list = []
                for i in delete_id_list:
                    robot_id = i[0]
                    timing_function_id = i[1]
                    timing_functions_obj = Robot2Timing.objects.filter(admin_user=request.user, robot_id=robot_id, timing_function_id=timing_function_id)
                    if timing_functions_obj:
                        timing_functions_obj_list.append(timing_functions_obj.first())

                if len(timing_functions_obj_list) != len(delete_id_list):
                    errcode = 4

            if errcode == None:
                # 如果正常则删除对应数据
                with transaction.atomic():
                    for timing_functions_obj in timing_functions_obj_list:
                        robot_id = timing_functions_obj.robot_id
                        timing_function_id = timing_functions_obj.timing_function_id
                        res = timing_functions_obj.delete()
                        if res[0] > 0:
                            logger.info(f"用户 [{request.user}] 执行删除定时任务 [{robot_id}-{timing_function_id}] 成功!")
                            errcode = 0
                        else:
                            logger.info(f"用户 [{request.user}] 执行删除定时任务 [{robot_id}-{timing_function_id}] 失败, 此前操作已回滚!")
                            errcode = 8
                            transaction.rollback()
                            break

        except Exception as e:
            errcode = 255
            logger.error(f"删除ROBOT TIMING记录时出错: {repr(e)}")
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
                    robot_id, timing_function_id = request.GET.get("id").split('==:::==')
                    robot_timing_obj = Robot2Timing.objects.filter(admin_user=request.user, robot_id=robot_id, timing_function_id=timing_function_id)

                    # 如果用户没有这个robot_timing_function, 则返回错误
                    if errcode == None:
                        if not robot_timing_obj:
                            errcode = 4

                    if errcode == None:
                        robot_timing_data = robot_timing_obj.first()

                        if robot_timing_data.timing_function_config:
                            timing_function_config_update = yaml.safe_dump(robot_timing_data.timing_function_config, allow_unicode=True, default_flow_style=False, sort_keys=False)
                        else:
                            timing_function_config_update = ""

                        form_initial_data = {
                            'robot_id_update': robot_timing_data.robot_id,
                            'timing_function_id_update': robot_timing_data.timing_function_id,
                            'timing_status_update': robot_timing_data.timing_status,
                            'timing_cron_update': robot_timing_data.timing_cron,
                            'timing_function_config_update': timing_function_config_update,
                        }

                        # 获取渲染后的HTML
                        html_list = [f'<form id="updateForm" robot-timing-function-id="{robot_timing_data.robot_id}==:::=={robot_timing_data.timing_function_id}">']
                        forms = RobotTimingUpdateForm(initial=form_initial_data)
                        for form_field in forms:
                            html_list.append(get_update_form_html(form_field, align_top_field=("timing_function_config_update")))
                        else:
                            html_list.append("</form>")

                        data = {"html": "\n".join(html_list)}
                        errcode = 0

        except Exception as e:
            errcode = 255
            logger.error(f"查询ROBOT TIMING配置时出错: {repr(e)}")
            logger.exception(e)

        # POST请求
        try:
            # ==========================================================================================================
            if request.method == 'POST':
                forms = RobotTimingUpdateForm(request.POST)

                if errcode == None:
                    if not forms.is_valid():
                        errcode = 1
                        data = forms.errors

                # 判断是否存在该robot_function
                if errcode == None:
                    robot_id, timing_function_id = request.POST.get("robot_timing_function_id").split('==:::==')
                    robot_timing_obj = Robot2Timing.objects.filter(admin_user=request.user, robot_id=robot_id, timing_function_id=timing_function_id)
                    if not robot_timing_obj:
                        errcode = 5

                if errcode == None:
                    # 获取数据

                    timing_function_config = yaml.safe_load(forms.cleaned_data.get("timing_function_config_update"))
                    if not isinstance(timing_function_config, (dict, list)):
                        timing_function_config = {}

                    new_data = {
                        'timing_status': int(forms.cleaned_data.get("timing_status_update")),
                        'timing_cron': forms.cleaned_data.get("timing_cron_update"),
                        'timing_function_config': timing_function_config,
                    }

                    res = robot_timing_obj.update(**new_data)
                    if res:
                        logger.info(f"用户 [{request.user}] 更新机器人功能配置成功! [{robot_timing_obj}] => {new_data}")
                        errcode = 0
                    else:
                        logger.info(f"用户 [{request.user}] 更新机器人功能配置失败! [{robot_timing_obj}] => {new_data}")
                        errcode = 7

        except Exception as e:
            errcode = 255
            logger.error(f"更新ROBOT TIMING配置时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})
