from django.db import models

# Create your models here.

class BaseModel(models.Model):
    status = models.BooleanField(default=True, verbose_name='状态')
    LastUpdateTime = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')

    class Meta:
        abstract = True  # 父类中必须指定该属性，否则该类会被创建到数据库


class Project(BaseModel):
    """
    项目表
    """
    ProjectType = (
        ('Web', 'Web'),
        ('App', 'App')
    )
    name = models.CharField(max_length=50, verbose_name='项目名称')
    version = models.CharField(max_length=50, verbose_name='版本')
    type = models.CharField(max_length=50, verbose_name='类型', choices=ProjectType)



    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        db_table="gy_pms_project"



class GlobalHost(BaseModel):
    """
    host域名
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目', related_name="project_host")
    name = models.CharField(max_length=50, verbose_name='名称')
    host = models.CharField(max_length=1024, verbose_name='Host地址')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'HOST'
        verbose_name_plural = 'HOST管理'
        db_table = "gy_pms_host"


class TestSuite(BaseModel):
    """
    测试用例集
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='项目', related_name="project_suite")
    name = models.CharField(max_length=50, verbose_name='名称')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'TESTSUITE'
        verbose_name_plural = 'TESTSUITE管理'
        db_table = "gy_tms_suite"

class TestCase(BaseModel):
    """
    测试用例集
    """
    suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, verbose_name='测试用例', related_name="suite_case")
    name = models.CharField(max_length=50, verbose_name='名称')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'TESTCASE'
        verbose_name_plural = 'TESTCASE管理'
        db_table = "gy_tms_case"

class API(BaseModel):
    """
    接口
    """
    method_choice = (
        ("POST", "POST"),
        ("GET", "GET"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
    )
    data_type_choice = (('formdata','formdata'),('raw','raw'))
    http_choice = (('HTTP', 'HTTP'), ('HTTPS', 'HTTPS'))
    case = models.ForeignKey(TestCase, on_delete=models.CASCADE, verbose_name='用例', related_name="case_api")
    name = models.CharField(max_length=50, verbose_name='名称')
    dataType = models.CharField(max_length=50, verbose_name='数据类型',choices=data_type_choice)
    http = models.CharField(max_length=50, verbose_name='协议名称',choices=http_choice)
    method = models.CharField(max_length=10, verbose_name='请求方法', choices=method_choice)
    url = models.CharField(max_length=100, verbose_name='接口地址')
    headers = models.TextField( blank=True, null=True,verbose_name='请求头')
    params = models.TextField( blank=True, null=True,verbose_name='表单数据')
    body = models.TextField( blank=True, null=True,verbose_name='源数据')



    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'TESTCASE'
        verbose_name_plural = 'TESTCASE管理'
        db_table = "gy_tms_api"


class APIAssert(BaseModel):
    """
    断言
    """
    assert_choice = (
        ("json","json"),
        ("status_code","status_code"),
        ("reg","reg"),
        ("contains","contains"),
    )
    api = models.ForeignKey(API, on_delete=models.CASCADE, verbose_name='接口', related_name="api_assert")
    case = models.ForeignKey(TestCase, on_delete=models.CASCADE, verbose_name='用例',
                             related_name="case_assert")
    suite = models.ForeignKey(TestSuite, on_delete=models.CASCADE, verbose_name='用例集',
                              related_name="suite_assert")
    type = models.CharField(max_length=50, verbose_name='断言方式', choices=assert_choice)
    pattern = models.CharField(max_length=50,blank=True, null=True, verbose_name='正则或者jsonpath表达式')
    expect = models.CharField(max_length=50, verbose_name='预期结果')


    def __unicode__(self):
        return self.expect

    def __str__(self):
        return self.expect
    class Meta:
        db_table = "gy_tms_assert"


class APIRelate(BaseModel):
    """
    断言
    """
    relate_choice = (
        ("json","json"),
        ("reg","reg"),
    )
    api = models.ForeignKey(API, on_delete=models.CASCADE, verbose_name='接口', related_name="api_relate")
    case = models.ForeignKey(TestCase,on_delete=models.CASCADE, verbose_name='用例', related_name="case_relate")
    suite = models.ForeignKey(TestSuite,on_delete=models.CASCADE, verbose_name='用例集', related_name="suite_relate")
    name = models.CharField(max_length=50, verbose_name='变量名')
    type = models.CharField(max_length=50, verbose_name='提取方式', choices=relate_choice)
    pattern = models.CharField(max_length=50, verbose_name='正则或者jsonpath表达式')
    value = models.TextField(blank=True, null=True, verbose_name='提取的值')



    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        db_table = "gy_tms_relate"
        unique_together=("case_id","name")

class APIResult(BaseModel):
    """
    执行结果
    """
    api = models.ForeignKey(API, on_delete=models.CASCADE, verbose_name='接口', related_name="api_result")
    request_method = models.CharField(blank=True, null=True,max_length=50, verbose_name='请求方法')
    request_url = models.TextField(blank=True, null=True,verbose_name='请求地址')
    request_headers = models.TextField(blank=True, null=True,verbose_name='请求头')
    request_body = models.TextField(blank=True, null=True,verbose_name='请求正文')
    status_code = models.CharField(blank=True, null=True,max_length=50, verbose_name='响应状态码')
    response_headers = models.TextField(blank=True, null=True,verbose_name='响应头')
    response_body = models.TextField(blank=True, null=True,verbose_name='响应正文')
    assert_result = models.BooleanField(blank=True, null=True,verbose_name='断言结果')

    class Meta:
        db_table = "gy_tms_result"



# class APIResultRelatetions(BaseModel):
#     '''
#     执行结果
#     '''
#     api = models.ForeignKey(API, on_delete=models.CASCADE, verbose_name='接口', related_name="api_api_result_relate")
#     result = models.ForeignKey(APIResult, on_delete=models.CASCADE, verbose_name='执行结果', related_name="result_api_result_relate")
#     assert_result = models.BooleanField(blank=True, null=True,verbose_name='断言结果')

