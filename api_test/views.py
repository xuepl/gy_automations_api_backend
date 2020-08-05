import json
import re
import threading
import time

import jsonpath
import requests

from django.contrib.auth.models import User
from django.contrib import auth

from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework import views

from api_test.api.api import run_api, form_to_json, create_data, dict_is_null, run_case
from utils.custom_permission import AdminPermission
from utils import custom_token
from utils import custom_pagination

from . import serializers
from . import models
from . import custom_filters


class SignUp(views.APIView):

    def post(self,request):
        data = request.data
        user = User.objects.create_user(**data)
        return Response({"code":20000,"message":"注册成功","data":serializers.SerializerUser(instance=user).data})


class Login(views.APIView):

    def post(self,request):
        data = request.data
        user = auth.authenticate(**data)
        t = custom_token.create_token(user.username)
        return Response({"code":20000,"message":"登录成功","data":t})






# 项目增删改查
class Projects(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filterset_class = custom_filters.ProjectFilter
    pagination_class = custom_pagination.PageNumberPagination



# 主机配置的增删改查
class GlobalHosts(viewsets.ModelViewSet):
    queryset = models.GlobalHost.objects.all()
    serializer_class = serializers.GlobalHostSerializer
    filterset_class = custom_filters.hostFilter
    pagination_class = custom_pagination.PageNumberPagination


    def create(self,request,*args,**kwargs):
        """
        新增项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        if "project_id" in data:
            project_id = data.pop("project_id")
            project = models.Project.objects.filter(id=project_id).first()
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            result = serializer.save(project=project)
            return Response(self.get_serializer(instance=result).data)
        else:
            return Response({"code":40001,"message":"project_id 不能为空","data":None})



# 测试用例集的增删改查
class TestSuite(viewsets.ModelViewSet):
    queryset = models.TestSuite.objects.all()
    serializer_class = serializers.TestSuiteSerializer
    pagination_class = custom_pagination.PageNumberPagination
    filterset_class = custom_filters.SuiteFilter

    def create(self,request,*args,**kwargs):
        """
        新增项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        if "project_id" in data:
            project_id = data.pop("project_id")
            project = models.Project.objects.filter(id=project_id).first()
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            result = serializer.save(project=project)
            return Response(self.get_serializer(instance=result).data)
        else:
            return Response({"code":40001,"message":"project_id 不能为空","data":None})


# 测试用例的增删改查
class TestCase(viewsets.ModelViewSet):
    queryset = models.TestCase.objects.all()
    serializer_class = serializers.TestCaseSerializer
    pagination_class = custom_pagination.PageNumberPagination
    filterset_class = custom_filters.CaseFilter


    def create(self,request,*args,**kwargs):
        """
        新增项目
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        if "suite_id" in data:
            suite_id = data.pop("suite_id")
            suite = models.TestSuite.objects.filter(id=suite_id).first()
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            result = serializer.save(suite=suite)
            return Response(self.get_serializer(instance=result).data)
        else:
            return Response({"code":40002,"message":"suite_id 不能为空","data":None})


# 接口用例增删改查
class API(viewsets.ModelViewSet):
    queryset = models.API.objects.all()
    serializer_class = serializers.APISerializer
    pagination_class = custom_pagination.PageNumberPagination

    def create(self,request,*args,**kwargs):
        """
        新增接口用例
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        if "case_id" not in data:
            return Response({"code": 40003, "message": "case_id 不能为空", "data": None})
        case_id = data.pop("case_id")
        case = models.TestCase.objects.filter(id=case_id).first()
        if "headers" in data:
            data["headers"] = form_to_json(data["headers"])

        if data["dataType"]== 'formdata' and "params" in data:
            data["params"] = form_to_json(data["params"])
            data["body"] = None
        elif(data["dataType"]== 'raw'):
            data["params"]=None
        else:
            data["body"] = None
            data["params"] = None

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        api = serializer.save(case=case)
        if "api_assert" in data:
            assert_data = data["api_assert"]
            create_data(api,assert_data,serializers.APIAssertSerializer,models.APIAssert)
        if "api_relate" in data:
            relate_data = data["api_relate"]
            try:
                create_data(api, relate_data, serializers.APIRelateSerializer,models.APIRelate)
            except:
                return Response({"code": 40006, "message": "重复的变量名", "data": None})
        return Response(self.get_serializer(instance=api).data)

    def update(self,request,*args,**kwargs):
        """
        新增接口用例
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data

        api = self.get_object()
        if api is None:
            return Response({"code": 400013, "message": "修改的接口请求不存在", "data": None})

        if "headers" in data:
            data["headers"] = form_to_json(data["headers"])

        if data["dataType"]== 'formdata' and "params" in data:
            data["params"] = form_to_json(data["params"])
            data["body"] = None
        elif(data["dataType"]== 'raw'):
            data["params"]=None
        else:
            data["body"] = None
            data["params"] = None

        serializer = self.get_serializer(instance=api,data=data)
        serializer.is_valid(raise_exception=True)
        api = serializer.save()
        if "api_assert" in data:
            assert_data = data["api_assert"]
            create_data(api,assert_data,serializers.APIAssertSerializer,models.APIAssert)
        if "api_relate" in data:
            relate_data = data["api_relate"]
            try:
                create_data(api, relate_data, serializers.APIRelateSerializer,models.APIRelate)
            except:
                return Response({"code": 40006, "message": "重复的变量名", "data": None})
        return Response(self.get_serializer(instance=api).data)


class RunAPI(views.APIView):
    def post(self,request):
        data = request.data
        return run_api(data["host_id"],data["api_id"])


class GetResult(views.APIView):

    def get(self,request,pk):
        result = models.APIResult.objects.filter(api_id=pk).last()
        s = serializers.APIResultSerializer(instance=result)
        return Response(s.data)

        pass


class RunCase(views.APIView):

    def post(self,request):
        data = request.data
        t = threading.Thread(target=run_case,args=(data["host_id"],data["case_id"]))
        t.start()
        return Response({"isRunCase":True})



