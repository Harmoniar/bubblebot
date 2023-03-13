import time
from loguru import logger
from django.utils.deprecation import MiddlewareMixin


class LogMiddle(MiddlewareMixin):
    # 日志处理中间件

    def process_request(self, request):
        # 请求时间
        request.request_time = time.time()

    def process_response(self, request, response):

        # 获取IP，如果有XFF头，则用XFF头的IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        post_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        # 不记录静态资源的访问日志
        if response.headers.get('Content-Type') in ('application/json', 'text/html', 'text/html; charset=utf-8'):
            log_data = {
                "post_ip": post_ip,
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "process_time": "{:.3f}s".format(time.time() - request.request_time),
            }

            logger.info(f"Request - info: {log_data}")

        return response
