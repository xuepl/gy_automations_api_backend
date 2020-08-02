from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler as drf_exception_handler

from utils.custom_response import CustomResponse

SYSTEM_EXCEPTIONS = {
    20000: "成功",
    20003: "参数校验不通过",
    40001:"参数不能为空",
    50000: "服务器内部错误"
}


def exception_handler(exc,context):
    """
    自定义异常处理
    :param exc: 别的地方抛的异常就会传给exc
    :param context: 字典形式。抛出异常的上下文(即抛出异常的出处;即抛出异常的视图)
    :return: Response响应对象
    """
    response = drf_exception_handler(exc,context)
    if response is None:
        # drf 处理不了的异常
        print('%s - %s - %s' % (context['view'], context['request'].method, exc))
        return CustomResponse({'detail': '服务器错误'}, code=50000,msg=SYSTEM_EXCEPTIONS[50000],status=status.HTTP_500_INTERNAL_SERVER_ERROR, exception=True)
    if isinstance(exc,ValidationError):
        message = ""
        data = response.data
        for key in data:
            message += ";".join(data[key])
        return CustomResponse(None,code=20003,msg=message)
    return response