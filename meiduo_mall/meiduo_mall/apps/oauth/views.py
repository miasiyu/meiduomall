from django.shortcuts import render,redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
from .models import OAuthQQUser
from django.contrib.auth import login,authenticate
from .utils import encode_openid,decode_openid
from django_redis import get_redis_connection
from users.models import User

#1,获取qq登陆界面
class QQLoginView(View):
    def get(self,request):
        #1,获取参数
        state = request.GET.get("next","/")

        #2,创建OAuthQQ对象
        oauth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                client_secret=settings.QQ_CLIENT_SECRET,
                redirect_uri=settings.QQ_REDIRECT_URI,
                state=state
                )

        #3,获取qq登陆页面
        login_url = oauth_qq.get_qq_url()

        #4,返回响应
        return http.JsonResponse({"login_url":login_url})

#2,绑定qq用户和美多用户
class QQAuthUserView(View):
    def get(self,request):
        #1,获取参数(code,state)
        code = request.GET.get("code")
        state = request.GET.get("state","/")

        #2,校验
        if not code:
            return http.HttpResponseForbidden("code丢失")

        #3,获取access_token
        oauth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                client_secret=settings.QQ_CLIENT_SECRET,
                redirect_uri=settings.QQ_REDIRECT_URI,
                state=state
                )
        try:
            access_token = oauth_qq.get_access_token(code)
        except Exception:
            return http.HttpResponseForbidden("code已过期")

        #4,获取openid
        openid = oauth_qq.get_open_id(access_token)

        #5,通过openid,查询qq授权用户
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)
        except Exception as e:
            #5,1 初次授权,加密openid,返回授权页面
            encrypt_openid = encode_openid(openid)
            context = {"token":encrypt_openid}
            return render(request,'oauth_callback.html',context=context)
        else:
            #6,1 非初次授权,获取美多用户
            user = oauth_qq_user.user

            #6,2 状态保持
            login(request,user)

            #6,3 返回响应
            response = redirect("/")
            response.set_cookie("username",user.username)
            return response

    def post(self,request):
        #1,获取参数
        openid = request.POST.get("access_token")
        mobile = request.POST.get("mobile")
        password = request.POST.get("pwd")
        sms_code = request.POST.get("sms_code")

        #2,校验参数
        #2,1 为空校验
        if not all([openid,mobile,password,sms_code]):
            return http.HttpResponseForbidden('参数不全')

        #2,2 校验openid
        openid = decode_openid(openid)

        if not openid:
            return http.HttpResponseForbidden("openid已过期")

        #2,3 短信验证码校验
        redis_conn = get_redis_connection("code")
        redis_sms_code = redis_conn.get("sms_code_%s"%mobile)
        if not redis_sms_code:
            return http.HttpResponseForbidden("短信验证码已过期")

        if sms_code != redis_sms_code.decode():
            return http.HttpResponseForbidden("短信验证码错误")

        #2,3 账号密码,正确性
        user = authenticate(request, username=mobile, password=password)

        #3,数据入库,判断用户对象
        if user:
            #3,1 创建qq授权对象
            oauth_qq_user = OAuthQQUser()

            #3,2 关联美多用户和 openid
            oauth_qq_user.user = user
            oauth_qq_user.openid = openid

            #3,3 入库
            oauth_qq_user.save()

            #3,4 状态保持,返回响应
            login(request,user)
            response = redirect('/')
            response.set_cookie("username",user.username)
            return response
        else:
            #4,1 创建美多用户
            user = User.objects.create_user(username=mobile,password=password)

            #4,2 创建qq授权对象
            oauth_qq_user = OAuthQQUser()

            #4,3 关联美多用户和openid,入库
            oauth_qq_user.user = user
            oauth_qq_user.openid = openid
            oauth_qq_user.save()

            #4,4 状态保持,返回响应
            login(request,user)
            response = redirect('/')
            response.set_cookie("username",user.username)
            return response
