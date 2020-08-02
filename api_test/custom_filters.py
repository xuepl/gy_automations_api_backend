from django_filters import rest_framework as filters
from . import models


class ProjectFilter(filters.FilterSet):
    # field_name要过滤的字段 lookup_expr要过滤的规则
    name = filters.CharFilter(field_name="name", lookup_expr='contains') # 对名字进行模糊查询

    class Meta:
        model=models.Project
        fields=['name'] # 指定查询参数

class hostFilter(filters.FilterSet):
    # field_name要过滤的字段 lookup_expr要过滤的规则
    project_id = filters.CharFilter(field_name="project_id")
    name = filters.CharFilter(field_name="name", lookup_expr='contains')  # 对名字进行模糊查询

    class Meta:
        model=models.GlobalHost
        fields=['project_id',"name"] # 指定查询参数

class SuiteFilter(filters.FilterSet):
    # field_name要过滤的字段 lookup_expr要过滤的规则
    project_id = filters.CharFilter(field_name="project_id")
    name = filters.CharFilter(field_name="name", lookup_expr='contains')  # 对名字进行模糊查询

    class Meta:
        model=models.TestSuite
        fields=['project_id','name'] # 指定查询参数


class CaseFilter(filters.FilterSet):
    # field_name要过滤的字段 lookup_expr要过滤的规则
    suite_id = filters.CharFilter(field_name="suite_id")
    name = filters.CharFilter(field_name="name", lookup_expr='contains')  # 对名字进行模糊查询

    class Meta:
        model=models.TestCase
        fields=['suite_id',"name"] # 指定查询参数
