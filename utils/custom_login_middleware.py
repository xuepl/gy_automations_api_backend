import json

from django.http import HttpResponse
from utils.custom_token import check_token

white_list=["/v01/login/","/v01/signup/", "/docs/"] # 白名单
black_list=["/v01/black/"]  # 黑名单
import re

class CustomLoginMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response
        # 配置和初始化
    def __call__(self, request):
        request_url = request.path_info
        for p in white_list:
            if request_url in p:
                response = self.get_response(request)
                return response
        for p in black_list:
            if request_url in p:
                response = HttpResponse()
                response.content= json.dumps({"code":29999,"message":"请求内容非法","data":None})
                response["Content-Type"]="application/json;charset=UTF-8"
                return response
        token = request.META.get("HTTP_TOKEN")  # 获取请求头中token的值
        if check_token(token):
            response = self.get_response(request)
            return response
        response = HttpResponse()
        response.content = json.dumps({"code": 20001, "message": "暂未登录或token已过期", "data": None})
        response["Content-Type"] = "application/json"
        return response
