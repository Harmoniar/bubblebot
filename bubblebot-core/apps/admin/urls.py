from django.urls import path
from . import views


login_urls = [
    path("login/", views.Login.as_view(), name="admin_login"),
    path("logout/", views.logout, name="admin_logout"),
]

# MAIN =============================================================

robot = [
    path("robot/", views.robot, name="admin_robot"),
    path("robot/api/query", views.RobotApi.query, name="admin_robot_query"),
    path("robot/api/delete", views.RobotApi.delete, name="admin_robot_delete"),
    path("robot/api/insert", views.RobotApi.insert, name="admin_robot_insert"),
    path("robot/api/update", views.RobotApi.update, name="admin_robot_update"),
]

robot_function = [
    path("robot/function", views.robot_function, name="admin_robot_function"),
    path("robot/function/api/query", views.RobotFunctionApi.query, name="admin_robot_function_query"),
    path("robot/function/api/delete", views.RobotFunctionApi.delete, name="admin_robot_function_delete"),
    path("robot/function/api/insert", views.RobotFunctionApi.insert, name="admin_robot_function_insert"),
    path("robot/function/api/update", views.RobotFunctionApi.update, name="admin_robot_function_update"),
]

robot_timing = [
    path("robot/timing", views.robot_timing, name="admin_robot_timing"),
    path("robot/timing/api/query", views.RobotTimingApi.query, name="admin_robot_timing_query"),
    path("robot/timing/api/delete", views.RobotTimingApi.delete, name="admin_robot_timing_delete"),
    path("robot/timing/api/insert", views.RobotTimingApi.insert, name="admin_robot_timing_insert"),
    path("robot/timing/api/update", views.RobotTimingApi.update, name="admin_robot_timing_update"),
]


main_urls = [path("home/", views.home, name="admin_home"), *robot, *robot_function, *robot_timing]

# MANAGE =============================================================

loginlog = [
    path("loginlog/", views.loginlog, name="admin_loginlog"),
    path("loginlog/api/query", views.LoginLogApi.query, name="admin_loginlog_query"),
]

function = [
    path("function/", views.function, name="admin_function"),
    path("function/api/query", views.FunctionApi.query, name="admin_function_query"),
    path("function/api/delete", views.FunctionApi.delete, name="admin_function_delete"),
    path("function/api/insert", views.FunctionApi.insert, name="admin_function_insert"),
    path("function/api/update", views.FunctionApi.update, name="admin_function_update"),
]

timing_function = [
    path("tfunction/", views.timing_function, name="admin_timing_function"),
    path("tfunction/api/query", views.TimingFunctionApi.query, name="admin_timing_function_query"),
    path("tfunction/api/delete", views.TimingFunctionApi.delete, name="admin_timing_function_delete"),
    path("tfunction/api/insert", views.TimingFunctionApi.insert, name="admin_timing_function_insert"),
    path("tfunction/api/update", views.TimingFunctionApi.update, name="admin_timing_function_update"),
]

component = [
    path("component/", views.component, name="admin_component"),
    path("component/api/query", views.ComponentApi.query, name="admin_component_query"),
]

manage_urls = [path("personal/", views.Personal.as_view(), name="admin_personal"), *loginlog, *function, *timing_function, *component]

# =============================================================

urlpatterns = [path("", views.empty_url, name="admin_empty_url"), *login_urls, *main_urls, *manage_urls]
