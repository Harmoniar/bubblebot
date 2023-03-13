import re
import datetime
import yaml
from loguru import logger
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..myforms.robotForm import RobotQueryForm
from ..myforms.robotForm import RobotInsertForm
from ..myforms.robotForm import RobotUpdateForm
from ..lib.pagination import Pagination
from ..lib.render import get_update_form_html, strint_convert_to_list, field_convert_to_icontains
from robot.models import Robots
from robot.models import Components


errors_info = {0: "成功", 1: "请求数据错误", 2: "请传入至少一条要删除的数据", 3: "添加失败, 你已添加过该机器人", 4: "机器人ID不存在", 5: "机器人原ID不存在", 6: "要更新的机器人ID已存在", 7: "更新失败", 8: "删除失败", 9: "创建失败", 255: "系统繁忙"}

strim_tail_query_repl = re.compile("_query$")


@login_required
def robot(request):
    query_forms = RobotQueryForm()
    insert_forms = RobotInsertForm()
    return render(request, 'main/robot.html', locals())


class RobotApi:
    # ============================================================================================
    @login_required
    def query(request):
        errcode = None
        data = {}
        res_json = {}
        try:
            forms = RobotQueryForm(request.GET)
            if errcode == None:
                if (request.method != 'GET') or (not request.is_ajax):
                    errcode = 255

            # 校验请求的数据
            if errcode == None:
                if not forms.is_valid():
                    errcode = 1

            # 获取请求的数据
            if errcode == None:
                forms.cleaned_data = {re.sub(strim_tail_query_repl, "", k): v for k, v in forms.cleaned_data.items()}

                # 生成过滤数据
                filter_conditions = {"admin_user_id": str(request.user)}
                robot_id = forms.cleaned_data.get("robot_id")
                if robot_id:
                    filter_conditions["robot_id"] = robot_id

                robot_status = forms.cleaned_data.get("robot_status")
                if robot_status in ("0", "1"):
                    robot_status = int(robot_status)
                    filter_conditions["robot_status"] = robot_status

                icontains_fileds = ['robot_name', 'comment', 'master_id']
                filter_conditions.update(field_convert_to_icontains(forms, icontains_fileds))

                filtered_data = Robots.objects.filter(**filter_conditions).order_by("id")

                # 生成分页数据
                page_index = int(forms.cleaned_data.get("page_index"))
                page_index = page_index if page_index >= 1 else 1
                per_page_num = int(forms.cleaned_data.get("per_page_num"))

                pager = Pagination(filtered_data, page_index, per_page_num)
                current_page_data = []
                for data in pager.current_page_data_list:
                    tmp_data = {}
                    tmp_data["robot_id"] = data.robot_id
                    tmp_data["robot_name"] = data.robot_name
                    tmp_data["master_id"] = data.master_id
                    tmp_data["robot_status"] = get_robot_status_html(data)
                    tmp_data["run_time"] = get_run_time(data.start_time) if data.start_time else "-"
                    tmp_data["comment"] = data.comment if data.comment else "-"
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
            logger.error(f"查询ROBOT记录时出错: {repr(e)}")
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
            forms = RobotInsertForm(request.POST)
            if errcode == None:
                if (request.method != 'POST') or (not request.is_ajax):
                    errcode = 255

            if errcode == None:
                if not forms.is_valid():
                    errcode = 1
                    data = forms.errors

            if errcode == None:
                # 查询提交的robot_id, 如果存在则返回错误信息, 如果不存在则创建
                robot_id = forms.cleaned_data.get("robot_id_insert")
                robot_obj = Robots.objects.filter(admin_user=request.user, robot_id=robot_id)
                if robot_obj:
                    errcode = 3

            if errcode == None:
                master_id_str = forms.cleaned_data.get("master_id_insert").strip(" ,|")
                if master_id_str:
                    master_id_list = [int(i.strip()) for i in master_id_str.split("|")]
                else:
                    master_id_list = []

                robot_data = {
                    'admin_user_id': str(request.user),
                    'robot_id': robot_id,
                    'robot_name': forms.cleaned_data.get("robot_name_insert"),
                    'master_id': master_id_list,
                    'robot_status': forms.cleaned_data.get("robot_status_insert"),
                    'comment': forms.cleaned_data.get("comment_insert"),
                }
                res = Robots.objects.create(**robot_data)
                if res:
                    logger.info(f"用户 [{request.user}] 执行创建机器人 [{robot_id}] 成功!")
                    errcode = 0
                else:
                    logger.info(f"用户 [{request.user}] 执行创建机器人 [{robot_id}] 失败!")
                    errcode = 9

        except Exception as e:
            errcode = 255
            logger.error(f"添加ROBOT记录时出错: {repr(e)}")
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
                # 查询出用户所有的符合条件的robot，如果数量和delete_id_list的数量对不上，则返回错误
                user_robots_obj = Robots.objects.filter(admin_user=request.user, robot_id__in=delete_id_list)
                if user_robots_obj.count() != len(delete_id_list):
                    errcode = 4

            if errcode == None:
                # 如果正常则删除对应数据
                res = user_robots_obj.delete()
                if res[0] > 0:
                    logger.info(f"用户 [{request.user}] 执行删除机器人 {delete_id_list} 成功!")
                    errcode = 0
                else:
                    logger.info(f"用户 [{request.user}] 执行删除机器人 {delete_id_list} 失败!")
                    errcode = 8

        except Exception as e:
            errcode = 255
            logger.error(f"删除ROBOT记录时出错: {repr(e)}")
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
                    robot_id = request.GET.get("id")
                    robot_obj = Robots.objects.filter(admin_user=request.user, robot_id=robot_id)

                    # 如果用户没有这个robot, 则返回错误
                    if errcode == None:
                        if not robot_obj:
                            errcode = 4

                    if errcode == None:
                        robot_data = robot_obj.first()
                        form_initial_data = {
                            'robot_id_update': robot_data.robot_id,
                            'robot_name_update': robot_data.robot_name,
                            'master_id_update': " | ".join([str(i) for i in robot_data.master_id]),
                            'robot_status_update': robot_data.robot_status,
                            'protocol_server_mode_update': robot_data.protocol_server_mode,
                            'protocol_server_config_update': yaml.safe_dump(robot_data.protocol_server_config, allow_unicode=True, default_flow_style=False, sort_keys=False)
                            if robot_data.protocol_server_config
                            else "",
                            'listen_msg_type_update': robot_data.listen_msg_type,
                            'trigger_mode_update': robot_data.trigger_mode,
                            'command_prefix_update': " | ".join(robot_data.command_prefix),
                            'user_function_permit_update': " | ".join(robot_data.user_function_permit),
                            'group_permit_mode_update': str(robot_data.group_permit_mode),
                            'group_whitelist_update': " | ".join([str(i) for i in robot_data.group_whitelist]),
                            'group_blacklist_update': " | ".join([str(i) for i in robot_data.group_blacklist]),
                            'user_blacklist_update': " | ".join([str(i) for i in robot_data.user_blacklist]),
                            'comment_update': robot_data.comment,
                        }

                        # 获取渲染后的HTML
                        html_list = [f'<form id="updateForm" original-robot-id="{robot_data.robot_id}">']
                        forms = RobotUpdateForm(initial=form_initial_data)
                        for form_field in forms:
                            html_list.append(
                                get_update_form_html(
                                    form_field, align_top_field=("protocol_server_config_update",), multi_select_fields=("trigger_mode_update", "listen_msg_type_update")
                                )
                            )
                        else:
                            html_list.append("</form>")

                        data = {"html": "\n".join(html_list)}
                        errcode = 0

        except Exception as e:
            errcode = 255
            logger.error(f"查询ROBOT配置时出错: {repr(e)}")
            logger.exception(e)

        # POST请求
        try:
            # ==========================================================================================================
            if request.method == 'POST':
                forms = RobotUpdateForm(request.POST)

                if errcode == None:
                    if not forms.is_valid():
                        errcode = 1
                        data = forms.errors

                # 判断用户是否有该robot
                if errcode == None:
                    original_robot_id = int(request.POST.get("original_robot_id"))
                    original_robot_obj = Robots.objects.filter(admin_user=request.user, robot_id=original_robot_id)
                    if not original_robot_obj:
                        errcode = 5

                # 如果要修改robot_id, 则判断目标robot_id是否已存在
                if errcode == None:
                    update_robot_id = int(forms.cleaned_data.get("robot_id_update"))
                    if update_robot_id != original_robot_id:
                        update_robot_obj = Robots.objects.filter(admin_user=request.user, robot_id=update_robot_id)
                        if update_robot_obj:
                            errcode = 6

                if errcode == None:
                    # 获取数据
                    list_str_fields = ("master_id_update", "user_blacklist_update", "group_blacklist_update", "group_whitelist_update")
                    list_data = strint_convert_to_list(forms, list_str_fields)

                    server_config = yaml.safe_load(forms.cleaned_data.get("protocol_server_config_update"))
                    if not isinstance(server_config, dict):
                        server_config = {}

                    listen_msg_type = [int(i) for i in forms.cleaned_data.get("listen_msg_type_update")]
                    trigger_mode = [int(i) for i in forms.cleaned_data.get("trigger_mode_update")]

                    command_prefix = [i.strip() for i in forms.cleaned_data.get("command_prefix_update").strip(" |").split("|") if i.strip()]
                    user_function_permit = [i.strip() for i in forms.cleaned_data.get("user_function_permit_update").strip(" |").split("|") if i.strip()]

                    new_data = {
                        'robot_id': update_robot_id,
                        'robot_name': forms.cleaned_data.get("robot_name_update"),
                        'master_id': list_data.get("master_id_update"),
                        'robot_status': int(forms.cleaned_data.get("robot_status_update")),
                        'comment': forms.cleaned_data.get("comment_update"),
                        'protocol_server_mode': int(forms.cleaned_data.get("protocol_server_mode_update")),
                        'protocol_server_config': server_config,
                        'listen_msg_type': listen_msg_type,
                        'trigger_mode': trigger_mode,
                        'command_prefix': command_prefix,
                        'user_function_permit': user_function_permit,
                        'group_permit_mode': int(forms.cleaned_data.get("group_permit_mode_update")),
                        'group_whitelist': list_data.get("group_whitelist_update"),
                        'group_blacklist': list_data.get("group_blacklist_update"),
                        'user_blacklist': list_data.get("user_blacklist_update"),
                    }

                    if new_data.get("robot_status") == 0 and original_robot_obj.first().start_time != None:
                        new_data["start_time"] = None

                    res = original_robot_obj.update(**new_data)

                    if res:
                        logger.info(f"用户 [{request.user}] 更新机器人配置成功! [{original_robot_id}] => {new_data}")
                        errcode = 0
                    else:
                        logger.info(f"用户 [{request.user}] 更新机器人配置失败! [{original_robot_id}] => {new_data}")
                        errcode = 7

        except Exception as e:
            errcode = 255
            logger.error(f"更新ROBOT配置时出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})


def get_run_time(start_time: datetime):
    # 现在时间时间 - 传入的时间
    return str(datetime.datetime.now() - start_time).split(".")[0]


def get_robot_status_html(data: dict):
    if data.robot_status == 1:
        components_obj_list = list(Components.objects.filter(component_role=1, component_status=1).values("running_msg"))
        if not components_obj_list:
            notice_text = "等待组件运行中..."
            blue = "text-warning"
        else:
            for components in components_obj_list:
                running_msg: dict = components.get("running_msg")
                if running_msg.get(data.admin_user_id):
                    robot_running_msg = running_msg[data.admin_user_id].get(str(data.robot_id))
                    if robot_running_msg:
                        notice_text = robot_running_msg
                        if notice_text == "RUNNING":
                            notice_text = "机器人正常运行中..."
                            blue = "text-green"
                            if not data.start_time:
                                # 如果启动了，且启动时间是空，则更新启动时间为当前时间
                                data.start_tme = datetime.datetime.now()
                                data.save()
                        else:
                            blue = "text-warning"
                            # 如果有启动时间，且机器人没有正常运行，则更新启动时间为None
                            if data.start_time:
                                data.start_tme = None
                                data.save()
                        break
            else:
                notice_text = "组件暂未运行机器人, 等待组件运行机器人中..."
                blue = "text-warning"

        robot_status_html = f"<span data-toggle='tooltip' data-placement='left' title='{notice_text}'>\
            <i class='fa-solid fa-circle-exclamation {blue} ml-1 mr-1'></i>已启用</span>"

    # 如果Robot非启动状态, 则HTMl为已停用
    else:
        robot_status_html = f"<span><i class='fa-solid fa-circle-exclamation text-red ml-1 mr-1'></i>已停用</span>"

    return robot_status_html
