from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

class MyLoginRequiredview(LoginRequiredMixin,View):
    login_url = "/login" #未登录,重定向的路径
    redirect_field_name = "next" #跳转的引用