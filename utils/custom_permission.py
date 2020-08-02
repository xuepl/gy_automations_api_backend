from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission # 导入权限基类
from django.contrib.auth.models import User

class AdminPermission(BasePermission):
    message="必须是超级用户才能访问"
    def has_permission(self, request, view):
        user = request.user
        if isinstance(user,AnonymousUser):
            return False
        u = User.objects.filter(username=user,is_superuser=1).first()
        if u is None:
            return False
        else:
            return True

class NonePermission(BasePermission):
    def has_permission(self, request, view):
        return True
