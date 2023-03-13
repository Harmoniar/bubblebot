import datetime
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from loguru import logger
from ..lib.cipher import aes_cipher
from ..models import Components



errors_info = {0: "健康状态上报成功", 1: "校验失败或JSON格式错误", 2: "参数不完整", 255: "系统繁忙"}


@logger.catch
@csrf_exempt
def health_report(request):
    errcode = None
    data = {}
    res_json = {}

    try:
        if request.method != 'POST':
            errcode = 255

        if errcode == None:
            # 解密数据
            try:
                decrypted_data: dict = aes_cipher.decrypt(request.body, is_json=True)
            except UnicodeDecodeError:
                errcode = 1
            except ValueError:
                errcode = 1

        if errcode == None:
            # 检查参数完整性
            required_fields = ("id", "role", "status", "running_msg")
            if not all(i in required_fields for i in decrypted_data):
                errcode = 2

        if errcode == None:
            # 更新组件信息

            # 生成更新数据
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            post_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            post_ip = post_ip if post_ip else "Unknown"
            component_data = {
                "component_id": decrypted_data.get("id"),
                "component_role": decrypted_data.get("role"),
                "component_ip": post_ip,
                "component_status": 1,
                "running_msg": decrypted_data.get("running_msg"),
                "last_report_time": datetime.datetime.now(),
            }
            # 通过组件id获取组件对象
            component_obj = Components.objects.filter(component_id=decrypted_data.get("id"))
            if component_obj:
                component_obj.update(**component_data)
            else:
                component_obj.create(**component_data)

            errcode = 0

    except Exception as e:
        errcode = 255
        logger.error(f"组件健康上报时出错: {repr(e)}")
        logger.exception(e)

    res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
    res_data = aes_cipher.encrypt(res_json)
    return HttpResponse(res_data)
