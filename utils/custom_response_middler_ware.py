class ResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
         # 配置和初始化

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):# 推荐
        request_url = request.path_info
        if 'v01' not in request_url:
            return response

        data= response.data
        if not (isinstance(data,dict) or isinstance(data,list)):
            data = str(data)
        res = {
            "code": 20000,
            "message": "操作成功",
            "data": data
        }
        if "code" in data:
            return response
        if request.method=='DELETE':
            res["message"] = "删除成功"
        elif(request.method=='GET'):
            res["message"] = "查询成功"
        elif(request.method=='POST'):
            res["message"] = "新增成功"
        elif (request.method == 'PUT'):
            res["message"] = "修改成功"
        else:
            pass
        response.data = res
        return response