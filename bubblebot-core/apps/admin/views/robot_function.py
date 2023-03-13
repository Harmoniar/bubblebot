import re
import yaml
from loguru import logger
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from ..myforms.robotFunctionForm import RobotFunctionQueryForm
from ..myforms.robotFunctionForm import RobotFunctionInsertForm
from ..myforms.robotFunctionForm import RobotFunctionUpdateForm
from ..lib.pagination import Pagination
from ..lib.render import get_update_form_html, field_convert_to_icontains
from robot.models import Robots
from robot.models import Functions
from robot.models import Robot2Function


errors_info = {0: "成功", 1: "请求数据错误", 2: "请传入至少一条要删除的数据", 3: "添加失败, 功能ID已存在", 4: "功能ID不存在", 5: "功能原ID不存在", 6: "要更新的功能ID已存在", 7: "更新失败", 8: "删除失败", 9: "机器人ID不存在", 255: "系统繁忙"}

strim_tail_query_repl = re.compile("_query$")


@login_required
def robot_function(request):
    # 获取用户所有机器人ID, 和现存所有已启用的功能ID
    user_robots = [(i.get("robot_id"), i.get("robot_id")) for i in Robots.objects.filter(admin_user=request.user).values("robot_id")]
    all_functions = [(i.get("function_id"), i.get("function_name")) for i in Functions.objects.filter(global_function_status=1).values("function_id", "function_name")]

    query_user_robots = [("", "")]
    query_user_robots.extend(user_robots)
    query_all_functions = [("", "")]
    query_all_functions.extend(all_functions)

    query_forms = []
    for field in RobotFunctionQueryForm():
        if field.name == "robot_id_query":
            field.field.widget.choices = query_user_robots

        elif field.name == "function_id_query":
            field.field.widget.choices = query_all_functions
        query_forms.append(field)

    insert_user_robots = [("", "请选择机器人ID")]
    insert_user_robots.extend(user_robots)
    insert_all_functions = [("", "请选择功能")]
    insert_all_functions.extend(all_functions)

    insert_forms = []
    for field in RobotFunctionInsertForm():
        if field.name == "robot_id_insert":
            field.field.widget.choices = insert_user_robots
        elif field.name == "function_id_insert":
            field.field.widget.choices = insert_all_functions
        insert_forms.append(field)

    return render(request, 'main/robot_function.html', locals())


class RobotFunctionApi:
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
                forms = RobotFunctionQueryForm(request.GET)
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

                function_id = forms.cleaned_data.get("function_name")
                if function_id:
                    filter_conditions["function_id"] = function_id

                function_status = forms.cleaned_data.get("function_status")
                if function_status in ("0", "1"):
                    function_status = int(function_status)
                    filter_conditions["function_status"] = function_status

                icontains_fileds = ['function.explain', 'trigger_command']
                filter_conditions.update(field_convert_to_icontains(forms, icontains_fileds))

                filtered_data = Robot2Function.objects.filter(**filter_conditions).order_by("id")

                # 生成分页数据
                page_index = int(forms.cleaned_data.get("page_index"))
                page_index = page_index if page_index >= 1 else 1
                per_page_num = int(forms.cleaned_data.get("per_page_num"))

                pager = Pagination(filtered_data, page_index, per_page_num)
                current_page_data = []
                for data in pager.current_page_data_list:
                    if data.function.global_function_status:
                        if data.function_status:
                            function_status_html = "<span class='dot bg-green d-inline-block mr-2'></span>已启用"
                        else:
                            function_status_html = "<span class='dot bg-red d-inline-block mr-2'></span>已禁用"
                    else:
                        function_status_html = "<span class='dot bg-red d-inline-block mr-2'></span>管理员禁用"

                    tmp_data = {}
                    tmp_data["robot_id"] = data.robot_id
                    tmp_data["function_id"] = data.function_id
                    tmp_data["function_name"] = data.function.function_name
                    tmp_data["function_status"] = function_status_html
                    tmp_data["explain"] = data.function.explain if data.function.explain else "-"
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
            logger.error(f"查询ROBOT FUNCTION记录时出错: {repr(e)}")
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
                forms = RobotFunctionInsertForm(request.POST)
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
                # 查询用户提交的function是否存在
                function_id = forms.cleaned_data.get("function_id_insert")
                function_obj = Functions.objects.filter(function_id=function_id)
                if not function_obj:
                    errcode = 4

            if errcode == None:
                # 查询用户提交的robot_function, 如果存在则返回错误信息, 如果不存在则创建
                robot_function_obj = Robot2Function.objects.filter(admin_user=request.user, robot_id=robot_id, function_id=function_id)
                if robot_function_obj:
                    errcode = 3

            if errcode == None:
                # 处理并生成数据并用于创建
                function_obj = function_obj.first()
                robot_function_data = {
                    'admin_user_id': str(request.user),
                    'robot_id': robot_id,
                    'function_id': function_id,
                    'function_status': forms.cleaned_data.get("function_status_insert"),
                    'trigger_command': function_obj.default_trigger_command,
                    'command_args': function_obj.default_command_args,
                    'trigger_template': function_obj.default_trigger_template,
                    'exception_template': function_obj.default_exception_template,
                }
                res = Robot2Function.objects.create(**robot_function_data)
                if res:
                    logger.info(f"用户 [{request.user}] 执行添加机器人功能 [{robot_id}-{function_id}] 成功!")
                    errcode = 0
                else:
                    logger.info(f"用户 [{request.user}] 执行添加机器人功能 [{robot_id}-{function_id}] 失败!")
                    errcode = 9

        except Exception as e:
            errcode = 255
            logger.error(f"添加ROBOT FUNCTION记录时出错: {repr(e)}")
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
                functions_obj_list = []
                for i in delete_id_list:
                    robot_id = i[0]
                    function_id = i[1]
                    functions_obj = Robot2Function.objects.filter(admin_user=request.user, robot_id=robot_id, function_id=function_id)
                    if functions_obj:
                        functions_obj_list.append(functions_obj.first())

                if len(functions_obj_list) != len(delete_id_list):
                    errcode = 4

            if errcode == None:
                # 如果正常则删除对应数据
                with transaction.atomic():
                    for functions_obj in functions_obj_list:
                        robot_id = functions_obj.robot_id
                        function_id = functions_obj.function_id
                        res = functions_obj.delete()
                        if res[0] > 0:
                            logger.info(f"用户 [{request.user}] 执行删除功能 [{robot_id}-{function_id}] 成功!")
                            errcode = 0
                        else:
                            logger.info(f"用户 [{request.user}] 执行删除功能 [{robot_id}-{function_id}] 失败, 此前操作已回滚!")
                            errcode = 8
                            transaction.rollback()
                            break

        except Exception as e:
            errcode = 255
            logger.error(f"删除ROBOT FUNCTION记录时出错: {repr(e)}")
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
                    robot_id, function_id = request.GET.get("id").split('==:::==')
                    robot_function_obj = Robot2Function.objects.filter(admin_user=request.user, robot_id=robot_id, function_id=function_id)

                    # 如果用户没有这个robot_function, 则返回错误
                    if errcode == None:
                        if not robot_function_obj:
                            errcode = 4

                    if errcode == None:
                        robot_function_data = robot_function_obj.first()
                        form_initial_data = {
                            'robot_id_update': robot_function_data.robot_id,
                            'function_id_update': robot_function_data.function_id,
                            'function_status_update': robot_function_data.function_status,
                            'trigger_command_update': " | ".join(robot_function_data.trigger_command),
                            'command_args_update': yaml.safe_dump(robot_function_data.command_args, allow_unicode=True, default_flow_style=False, sort_keys=False)
                            if robot_function_data.command_args
                            else "",
                            'trigger_template_update': yaml.safe_dump(robot_function_data.trigger_template, allow_unicode=True, default_flow_style=False, sort_keys=False)
                            if robot_function_data.trigger_template
                            else "",
                            'exception_template_update': yaml.safe_dump(robot_function_data.exception_template, allow_unicode=True, default_flow_style=False, sort_keys=False)
                            if robot_function_data.exception_template
                            else "",
                        }

                        # 获取渲染后的HTML
                        html_list = [f'<form id="updateForm" robot-function-id="{robot_function_data.robot_id}==:::=={robot_function_data.function_id}">']
                        forms = RobotFunctionUpdateForm(initial=form_initial_data)
                        for form_field in forms:
                            html_list.append(get_update_form_html(form_field, align_top_field=("command_args_update", "trigger_template_update", "exception_template_update")))
                        else:
                            html_list.append("</form>")

                        data = {"html": "\n".join(html_list)}
                        errcode = 0

        except Exception as e:
            errcode = 255
            logger.error(f"查询ROBOT FUNCTION配置时出错: {repr(e)}")
            logger.exception(e)

        # POST请求
        try:
            # ==========================================================================================================
            if request.method == 'POST':
                forms = RobotFunctionUpdateForm(request.POST)

                if errcode == None:
                    if not forms.is_valid():
                        errcode = 1
                        data = forms.errors

                # 判断是否存在该robot_function
                if errcode == None:
                    robot_id, function_id = request.POST.get("robot_function_id").split('==:::==')
                    robot_function_obj = Robot2Function.objects.filter(admin_user=request.user, robot_id=robot_id, function_id=function_id)
                    if not robot_function_obj:
                        errcode = 5

                if errcode == None:
                    # 获取数据
                    trigger_command_str = forms.cleaned_data.get("trigger_command_update").strip(" ,|")
                    if trigger_command_str:
                        trigger_command_list = [i.strip() for i in trigger_command_str.split("|")]
                    else:
                        trigger_command_list = []

                    trigger_template = yaml.safe_load(forms.cleaned_data.get("trigger_template_update"))
                    if not isinstance(trigger_template, (dict, list)):
                        trigger_template = {}

                    exception_template = yaml.safe_load(forms.cleaned_data.get("exception_template_update"))
                    if not isinstance(exception_template, (dict, list)):
                        exception_template = {}

                    new_data = {
                        'function_status': int(forms.cleaned_data.get("function_status_update")),
                        'trigger_command': trigger_command_list,
                        'trigger_template': trigger_template,
                        'exception_template': exception_template,
                    }

                    res = robot_function_obj.update(**new_data)
                    if res:
                        logger.info(f"用户 [{request.user}] 更新机器人功能配置成功! [{robot_function_obj}] => {new_data}")
                        errcode = 0
                    else:
                        logger.info(f"用户 [{request.user}] 更新机器人功能配置失败! [{robot_function_obj}] => {new_data}")
                        errcode = 7

        except Exception as e:
            errcode = 255
            logger.error(f"更新ROBOT FUNCTION配置时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})
