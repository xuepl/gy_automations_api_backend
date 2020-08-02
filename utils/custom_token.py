import time
from django.core import signing
import hashlib
from django_redis import get_redis_connection

cache = get_redis_connection("default")
HEADER = {'typ': 'JWT', 'alg': 'default'}
KEY = 'GUOYASOFT'
SALT = 'www.guoyasoft.com'
TIME_OUT = 30 * 60  # 2min


def encrypt(obj):
    """加密"""
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def decrypt(src):
    """解密"""
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    return raw


def create_token(username):
    """生成token信息"""
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload
    payload = {"username": username, "iat": time.time()}
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 存储到缓存中
    cache.set(username, token, TIME_OUT)
    return token


def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


# 通过token获取用户名
def get_username(token):
    payload = get_payload(token)
    return payload['username']


def check_token(token):
    if token is None:
        return False
    username = get_username(token)
    last_token = cache.get(username)
    if last_token:
        cache.expire(username, TIME_OUT)
        return True
    return False


def delete_token(username):
    last_token = cache.get(username)
    if last_token:
        cache.delete(username)
        return True
    return False