from itsdangerous.jws import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings

#1,加密openid
def encode_openid(openid):
    #1,创建加密对象
    serializer = TJWSSerializer(secret_key=settings.SECRET_KEY,expires_in=300)

    #2,加密数据
    token = serializer.dumps({"openid":openid})

    #3,返回响应
    return token.decode()

#2,解密openid
def decode_openid(data):
    #1,创建加密对象
    serializer = TJWSSerializer(secret_key=settings.SECRET_KEY,expires_in=300)

    #2,加密数据
    try:
        dict_data = serializer.loads(data)
    except Exception as e:
        return None

    #3,返回响应
    return dict_data.get("openid")
