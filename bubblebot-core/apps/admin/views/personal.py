import time
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from loguru import logger
from ..myforms.personalForm import ModifyPersonalInfoForm


errors_info = {
    0: "个人信息变更成功！",
    1: "校验失败",
    255: "系统繁忙",
}


class Personal(View):
    @method_decorator(login_required)
    def get(self, request):
        personal_forms = ModifyPersonalInfoForm(initial={"username": request.user.username})
        return render(request, "manage/personal.html", locals())

    @method_decorator(login_required)
    def post(self, request):
        errcode = None
        info = None
        data = {}
        res_json = {}

        try:
            form = ModifyPersonalInfoForm(request.POST)

            # 校验成功则修改信息，否则返回报错信息
            if errcode == None:
                if not form.is_valid():
                    errcode = 1
                    data = form.errors

            # 判断是否要更新密码，如果要则判断老密码是否正确
            if errcode == None:
                if form.cleaned_data.get('new_password') and (not request.user.check_password(form.cleaned_data.get('old_password'))):
                    errcode = 1
                    form.add_error("old_password", "原密码错误，请重新输入")
                    data = form.errors

            # 如果有头像，则判断图片是否符合条件
            if errcode == None:
                avatar_obj = request.FILES.get("avatar")
                if avatar_obj:
                    check_res = check_img(avatar_obj)
                    # 如果校验通过，则修改图片文件名，以防上传后与之前上传过的文件重名
                    if check_res == 0:
                        time_stamp = str(time.time()).replace(".", "")
                        file_suffix = avatar_obj.content_type.rsplit("/", 1)[-1]
                        avatar_obj._name = "{}.{}".format(time_stamp, file_suffix)
                    else:
                        if check_res == 1:
                            form.add_error("avatar", "头像图片格式错误，请确保上传的文件是否是图片")
                        if check_res == 2:
                            form.add_error("avatar", "头像图片文件过大，最大允许上传的文件大小为5MB")
                        errcode = 1
                        data = form.errors

                # # 更新数据
            if errcode == None:
                update_data = {}
                # 有则更新，没有则忽视
                avatar_obj = request.FILES.get("avatar")
                if avatar_obj:
                    update_data["avatar"] = avatar_obj
                if form.cleaned_data.get('username'):
                    update_data["username"] = form.cleaned_data.get('username')
                if form.cleaned_data.get('new_password'):
                    update_data["new_password"] = form.cleaned_data.get('new_password')

                # 更新用户信息
                for k, v in update_data.items():
                    if k == 'new_password':
                        user_obj = request.user
                        request.user.set_password(v)
                        update_session_auth_hash(request, user_obj)
                    else:
                        setattr(request.user, k, v)
                request.user.save()

                errcode = 0

        except Exception as e:
            errcode = 255
            logger.error(f"个人信息变更出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
        return JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})


def check_img(file_obj):

    if not file_obj.content_type.startswith("image/"):
        return 1

    # 5MB(5 * 1024 * 1024 = 5242880)
    if file_obj.size > 5242880:
        return 2

    return 0
