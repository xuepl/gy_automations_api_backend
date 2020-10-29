# 获取主机地址
import json
import re
import time

import jsonpath
import requests
from django.utils import timezone
from rest_framework.response import Response

from .. import models
from .. import serializers


def get_host(host_id):
    host = models.GlobalHost.objects.filter(id=host_id).first().host
    if not (host.startswith("http://") or host.startswith("https://")):
        host = "http://" + host
    return host


# 替换接口请求数据中的变量${变量名}
def replate_variable(data,vars):
    if isinstance(data, dict):
        for k in data:
            data[k] = replate_variable(data[k],vars)
        return data
    elif isinstance(data,list):
        for i in range(len(data)):
            data[i] = replate_variable(data[i],vars)
        return data
    elif isinstance(data, str):
        r = re.compile(r"\${(.*?)}")
        for v in r.findall(data):
            if v in vars:
                data = data.replace("${" + v + "}", vars[v])
        return data
    else:
        return data

# 获取接口请求信息
def get_api_info(api_id):
    api = models.API.objects.filter(id=api_id).first()
    if api is None:
        return None
    method = api.method
    url = api.url
    headers=None
    if api.headers:
        h = json.loads(api.headers)
        headers = {k:l[k] for l in h for k in l}
    params=None
    if api.params:
        h = json.loads(api.params)
        params = {k:l[k] for l in h for k in l}
    body = api.body
    data = get_case_relates(api_id)

    return method,replate_variable(url,data),replate_variable(headers,data),replate_variable(params,data),replate_variable(body,data)

def run_case(host_id, case_id):
    apis = models.TestCase.objects.get(id=case_id).case_api.all()
    for api in apis:
        run_api(host_id,api.id)


# 运行接口用例
def run_api(host_id, api_id):
    host = get_host(host_id)
    if host is None:
        return Response({"code":50010,"message":"主机配置不存在","data":None})
    api = get_api_info(api_id)
    if api is None:
        return Response({"code": 50011, "message": "接口用例不存在", "data": None})
    method, url, headers, params, body = api
    url = host + url

    if params and (method == "GET" or method == "DELETE"):
        r = requests.request(method=method,url=url,headers=headers,params=params)
    elif params:
        r = requests.request(method=method, url=url, headers=headers, data=params)
    elif body:
        r = requests.request(method=method, url=url, headers=headers, data=body.encode('utf-8'))
    else:
        r = requests.request(method=method, url=url, headers=headers)
    save_request_result(api_id,r)
    result = models.APIResult.objects.filter(api_id=api_id).last()
    return Response(serializers.APIResultSerializer(instance=result).data)

# 保存测试结果
def save_request_result(api_id,response):
    api = models.API.objects.get(id=api_id)
    r = response
    data = {}
    data["request_method"] = r.request.method
    data["request_url"] = r.request.url
    data["request_headers"] = json.dumps(dict(r.request.headers))

    data["request_body"] = r.request.body.decode('utf-8') if r.request.body else ""
    data["status_code"] = r.status_code
    data["response_headers"] = json.dumps(dict(r.headers))
    data["response_body"] = r.text
    data["assert_result"] = response_assert(api_id,data)
    response_relate(api_id,data)
    s = serializers.APIResultSerializer(data=data)
    s.is_valid(raise_exception=True)
    s.save(api=api)

# 接口响应变量提取
def response_relate(api_id, data):
    api = models.API.objects.get(id=api_id)
    relates = models.APIRelate.objects.filter(api_id=api.id)
    for r in relates:
        pattern = r.pattern
        if r.type == 'json':
            value = parse_json_path(pattern,data["response_body"])
        elif r.type == 'reg':
            value = parse_regular(pattern,data["response_body"])
        else:
            value = None
        s = serializers.APIRelateSerializer(data={"value": value}, instance=r, partial=True)
        s.is_valid(raise_exception=True)
        s.save()


# 响应断言
def response_assert(api_id, data):
    api = models.API.objects.get(id=api_id)
    assertes = models.APIAssert.objects.filter(api_id=api.id)
    for a in assertes:
        if a.type == "json" and a.expect not in parse_json_path(a.pattern,data["response_body"]):
            return False
        elif a.type == "status_code" and str(a.expect) != str(data["status_code"]):
            return False
        elif a.type == "reg" and a.expect not in parse_regular(a.pattern,data["response_body"]):
            return False
        elif a.type == "contains" and a.expect not in data["response_body"]:
            return False
    return True


# 解析正则 表达式
def parse_regular(reg,data):
    r = re.compile(reg)
    res = r.findall(data)
    if len(res) == 0:
        return None
    return res[0]


# 解析jsonpath
def parse_json_path(json_path, json_string):
    res = jsonpath.jsonpath(json.loads(json_string), json_path)
    if len(res) == 0:
        return None
    return res[0]


# 获取当前用例下所有的关联变量
def get_case_relates(api_id):
    case_id = models.API.objects.get(id = api_id).case_id
    relates = models.APIRelate.objects.select_related("case").filter(case_id=case_id,status=1).exclude(api_id=api_id)
    data = {}
    for r in relates:
        if r.value is None:
            continue
        data[r.name]=r.value
    return data


# 表单数据转json字符串

def form_to_json(form):
    d = [{d["name"]: d["value"]} for d in form if d["name"] != '' and d["value"] != '']
    return json.dumps(d)

# 发序列化非空数据
def create_data(api,data,serializer,model):
    flag = timezone.now()
    if not isinstance(data,list):
        return False
    for d in data:
        if not dict_is_null(d):
            continue
        model.objects.filter(api_id=api.id, createTime__lt=flag).delete()
        s = serializer(data=d)
        s.is_valid(raise_exception=True)
        s.save(api=api,case=api.case, suite=api.case.suite)
    return True


# 判断字典的value是否存在为空的
def dict_is_null(d):
    for k in d:
        if k in ["type",'name','expect'] and d[k] == "":
            return False
    return True
