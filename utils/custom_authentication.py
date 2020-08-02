from rest_framework.authentication import BaseAuthentication

from utils.custom_token import check_token, get_username


class CustomeAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth = request.META.get('HTTP_TOKEN', None)
        if not auth:
            return None  # 返回一个user和token值，token值可以为空
        auth_list = auth.split()
        if not (len(auth_list) == 2 and auth_list[0] == 'token'):
            return None
        key = auth_list[1]
        if (check_token(key)):
            return get_username(key),key
        else:
            return None

    def authenticate_header(self, request):
        return

        pass



