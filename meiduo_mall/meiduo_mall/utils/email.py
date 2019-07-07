from itsdangerous.jws import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings
from users.models import User
#1,生成验证码的邮件链接
def generate_verify_url(user):

    #1,拼接用户信息
    token = {
        "user_id":user.id,
        "email":user.email
    }

    #2,加密用户数据
    serializer = TJWSSerializer(secret_key=settings.SECRET_KEY,expires_in=300)
    token  = serializer.dumps(token)

    #3,拼接token
    verify_url = "%s?token=%s"%(settings.EMAIL_VERIFY_URL,token.decode())

    #4,返回
    return verify_url

#2,解密token
def decode_token(token):
    #1,创建解密对象
    serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=300)

    #2,调用loads方法解密
    try:
        dict_data = serializer.loads(token)

        #获取用户对象
        user = User.objects.get(id=dict_data.get("user_id"))
    except Exception as e:
        return None


    #3,返回数据
    return user