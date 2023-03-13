from datetime import datetime
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import FieldError, FieldDoesNotExist
from django.db.utils import IntegrityError
from loguru import logger
from ..lib.cipher import aes_cipher
from .. import models as robot_models

errors_info = {
    0: "操作成功",
    1: "校验失败或JSON格式错误",
    2: "参数不完整",
    3: "参数中有不存在的方法",
    4: "参数中有不存在的模型",
    5: "过滤条件字段类型错误",
    6: "数据字段类型错误",
    7: "过滤字段中有不存在的字段",
    8: "未查询到相关数据",
    9: "查询字段中有不存在的字段",
    10: "主键已被使用或缺少必须的字段",
    11: "数据字段中存在表没有的字段",
    12: "数据字段中存在不符合类型的值",
    13: "删除操作必须指定过滤条件",
    255: "系统繁忙",
}


@csrf_exempt
def curd_api(request):
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
            except UnicodeDecodeError as e:
                errcode = 1
            except ValueError as e:
                errcode = 1

        if errcode == None:
            # 检查参数完整性
            required_fields = ("method", "model_name", "filter_conditions", "data")
            if not all(i in required_fields for i in decrypted_data):
                errcode = 2

        if errcode == None:
            # 检查参数正确性
            if decrypted_data.get("method") not in ("query", "create", "delete", "update"):
                errcode = 3
            elif decrypted_data.get("model_name") not in robot_models.__dict__.keys():
                errcode = 4
            elif (decrypted_data.get("method") in ("query", "delete", "update")) and (not isinstance(decrypted_data.get("filter_conditions"), dict)):
                errcode = 5
            elif (decrypted_data.get("method") == "query") and (not isinstance(decrypted_data.get("data"), list)):
                errcode = 6
            elif (decrypted_data.get("method") in ("create", "update")) and (not isinstance(decrypted_data.get("data"), dict)):
                errcode = 6

        if errcode == None:
            # 先按照条件查询出数据对象
            data_model = getattr(robot_models, decrypted_data.get("model_name"))

            if decrypted_data.get("method") in ("query", "delete", "update"):
                try:
                    data_obj = data_model.objects.filter(**decrypted_data.get("filter_conditions"))
                except FieldError:
                    errcode = 7

        if errcode == None:
            # 执行相关操作
            # ============================= 查 =============================
            if decrypted_data.get("method") == "query":
                try:
                    queried_data = data_obj.values(*decrypted_data.get("data"))
                    data = []
                    # 由于json不支持datetime类型, 所以需要转换为字符串时间
                    for i in queried_data:
                        tmp_data = {}
                        for k, v in i.items():
                            if isinstance(v, datetime):
                                v = v.strftime("%Y-%m-%d %H:%M:%S")
                            tmp_data[k] = v
                        data.append(tmp_data)
                    errcode = 0
                except FieldError:
                    errcode = 9

            # ============================= 增 =============================
            elif decrypted_data.get("method") == "create":
                try:
                    data_model.objects.create(**decrypted_data.get("data"))
                    errcode = 0
                except IntegrityError:
                    errcode = 10
                except TypeError:
                    errcode = 11
                except ValueError:
                    errcode = 12

            # ============================= 删 =============================
            elif decrypted_data.get("method") == "delete":
                if not data_obj:
                    errcode = 8
                elif not decrypted_data.get("filter_conditions"):
                    errcode = 13
                else:
                    data_obj.delete()
                    errcode = 0

            # ============================= 改 =============================
            elif decrypted_data.get("method") == "update":
                if not data_obj:
                    errcode = 8
                else:
                    try:
                        data_model.objects.update(**decrypted_data.get("data"))
                        errcode = 0
                    except FieldDoesNotExist:
                        errcode = 11
                    except ValueError:
                        errcode = 12

    except Exception as e:
        errcode = 255
        logger.error(f"执行CURD API操作时出错: {repr(e)}")
        logger.exception(e)

    res_json = {"errcode": errcode, "info": errors_info.get(errcode), "data": data}
    res_data = aes_cipher.encrypt(res_json)
    return HttpResponse(res_data)
