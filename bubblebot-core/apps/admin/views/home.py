from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from ..models import UserLoginLog


@login_required
def home(request):
    user_login_logs = UserLoginLog.objects.filter(login_user=request.user).order_by("-id")[0:5]
    user_robots = request.user.robots_set.all()

    return render(request, 'main/home.html', locals())


# 退出登录
@login_required
def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect("admin_login")
