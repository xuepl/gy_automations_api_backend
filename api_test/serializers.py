from rest_framework import serializers
from django.contrib.auth.models import User

from . import models

class SerializerUser(serializers.ModelSerializer):

    class Meta:
        model=User
        # fields=["id","username","email"]
        fields="__all__"


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目信息序列化
    """
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)


    class Meta:
        model = models.Project
        fields = ('id', 'name', 'version', 'type', 'status', 'LastUpdateTime', 'createTime',  'description')


class GlobalHostSerializer(serializers.ModelSerializer):
    """
    host信息序列化
    """
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)


    class Meta:
        model = models.GlobalHost
        fields = ('id', 'project_id', 'name', 'host', 'status', 'description',"LastUpdateTime","createTime")



class APIAssertSerializer(serializers.ModelSerializer):
    """
    断言信息序列化
    """
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)


    class Meta:
        model = models.APIAssert
        fields = ('id', 'api_id', 'type',"pattern","expect", 'status', 'description',"LastUpdateTime","createTime")



class APIRelateSerializer(serializers.ModelSerializer):
    """
    断言信息序列化
    """
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)


    class Meta:
        model = models.APIRelate
        fields = ('id', 'api_id', 'name',"type", 'pattern', 'value', 'description',"LastUpdateTime","createTime")


class APISerializer(serializers.ModelSerializer):
    """
    接口信息序列化
    """
    api_assert = APIAssertSerializer(many=True,read_only=True)
    api_relate = APIRelateSerializer(many=True,read_only=True)
    result = serializers.SerializerMethodField(read_only=True)
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    def get_result(self,obj):
        sql = "SELECT * FROM `gy_tms_result` WHERE createTime > DATE_SUB(NOW(),INTERVAL 5 MINUTE) and api_id={};".format(obj.id)
        result = models.APIAssert.objects.raw(sql)
        if len(result) == 0:
            return 2  # 未运行
        res = result[len(result) - 1]
        if res is None:
            return 2 # 未运行
        elif res.assert_result:
            return 1 # 运行成功
        else:
            return 0 # 运行失败


    class Meta:
        model = models.API
        fields = ('id', 'case_id', 'name','http','dataType','result',"method", "url", "headers", "params", "body", 'status','api_assert','api_relate', 'description',"LastUpdateTime","createTime")

class TestCaseSerializer(serializers.ModelSerializer):
    """
    测试用例信息序列化
    """
    api_list = serializers.SerializerMethodField()
    api_count = serializers.SerializerMethodField()
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    def get_api_count(self,obj):
        return obj.case_api.all().count()

    def get_api_list(self,obj):
        api_objs = obj.case_api.all()
        return [{"id": a.id,"name":a.name,"method":a.method,"url":a.url,"status":a.status} for a in api_objs]


    class Meta:
        model = models.TestCase
        fields = ('id', 'suite_id','api_count','api_list', 'name',  'status', 'description',"LastUpdateTime","createTime")

class TestSuiteSerializer(serializers.ModelSerializer):
    """
    测试用例集信息序列化
    """
    case_list = serializers.SerializerMethodField()
    case_count = serializers.SerializerMethodField()
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = models.TestSuite
        fields = ('id', 'project_id','case_count','case_list', 'name',  'status', 'description',"LastUpdateTime","createTime")
    def get_case_count(self,obj):
        return obj.suite_case.all().count()

    def get_case_list(self,obj):
        case_objs = obj.suite_case.all()
        return [{"id":c.id,"name":c.name,"status":c.status} for c in case_objs]




class APIResultSerializer(serializers.ModelSerializer):
    """
    断言信息序列化
    """
    LastUpdateTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    createTime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    assert_list = serializers.SerializerMethodField(read_only=True)
    relate_list = serializers.SerializerMethodField(read_only=True)
    def get_assert_list(self,obj):
        results = obj.api.api_assert.all()
        return [{"type":a.type,"pattern":a.pattern,"expect":a.expect} for a in results]
    def get_relate_list(self,obj):
        results = obj.api.api_relate.all()
        return [{"type":a.type,"name":a.name,"pattern":a.pattern,"value":a.value} for a in results]


    class Meta:
        model = models.APIResult
        fields = ('id', 'api_id',"assert_list",'relate_list', 'request_method',"request_url", 'request_headers', 'request_body','status_code','response_headers','response_body','assert_result', 'description',"LastUpdateTime","createTime")
