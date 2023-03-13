from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.contrib import auth
from loguru import logger
from ..myforms.loginForm import LoginForm
from ..models import IpMapLocation
from ..models import UserLoginLog


errors_info = {
    0: "登录成功",
    1: "校验错误",
    2: "用户不存在或密码错误",
}


class Login(View):
    def get(self, request):
        useremail = request.COOKIES.get("fastd_useremail")
        password = request.COOKIES.get("fastd_password")
        is_remember = request.COOKIES.get("fastd_remember")

        if not useremail:
            useremail = ""
        if not password:
            password = ""

        login_forms = LoginForm(initial={"useremail": useremail, "password": password})

        return render(request, "login.html", locals())

    def post(self, request):
        errcode = None
        data = {}
        res_json = {}

        try:
            form = LoginForm(request.POST)
            useremail = request.POST.get('useremail')
            password = request.POST.get('password')
            remember = request.POST.get('remember')

            # 校验请求的数据
            if errcode == None:
                if not form.is_valid():
                    data = form.errors
                    errcode = 1

            # 判断是否ajax请求或是否携带ip
            if errcode == None:
                # 获取IP，如果有XFF头，则用XFF头的IP
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                post_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

                if (not request.is_ajax()) or (not post_ip):
                    errcode = 255

            # 验证用户邮箱和用户密码
            if errcode == None:
                user_obj = auth.authenticate(request, username=useremail, password=password)
                if user_obj:
                    auth.login(request, user_obj)
                    errcode = 0
                    data["next_url"] = reverse("admin_home")
                else:
                    errcode = 2

        except Exception as e:
            errcode = 255
            logger.error(f"登录校验出错: {repr(e)}")
            logger.exception(e)

        res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}

        response = JsonResponse(res_json, json_dumps_params={"ensure_ascii": False})
        response.set_cookie("fastd_useremail", useremail, expires=2592000)

        if remember == 'true' and errcode == 0:
            response.set_cookie("fastd_password", password, expires=2592000)
            response.set_cookie("fastd_remember", remember, expires=2592000)
        else:
            response.delete_cookie("fastd_password")
            response.delete_cookie("fastd_remember")

        # 如果存在用户名，则记录登录日志
        if errcode in (0, 2):
            record_login_log(useremail, post_ip, errcode)

        return response


def record_login_log(useremail, post_ip: str, errcode: int):
    # 获取IP位置
    binary_ip = ''.join('{:08b}'.format(int(i)) for i in post_ip.split('.'))
    location_obj = IpMapLocation.objects.filter(binary_start_ip__lte=binary_ip, binary_end_ip__gte=binary_ip).values("location").first()
    if location_obj:
        ip_location = location_obj.get("location")
    else:
        ip_location = "未知"

    # 获取登录状态
    if errcode == 0:
        login_result = 0
    else:
        login_result = 1

    UserLoginLog.objects.create(login_user_id=useremail, login_ip=post_ip, login_location=ip_location, login_result=login_result)
