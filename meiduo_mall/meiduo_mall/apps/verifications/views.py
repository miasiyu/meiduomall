from django.shortcuts import render
from django.views import View
from django import http
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
import random
#1,生成图片验证码
from meiduo_mall.libs.yuntongxun.sms import CCP
from meiduo_mall.utils.response_code import RET
from verifications import constants

#1,图片验证码
class ImageCodeView(View):
    def get(self,request,image_code_id):
        #1,生成图片验证码
        name,text,image_data = captcha.generate_captcha()

        #2,保存图片验证码到redis中
        redis_conn = get_redis_connection("code")
        #参数1: 保存到redis键,  参数2: 有效期,  参数3: 值
        redis_conn.setex("img_code_%s"%image_code_id,constants.REDIS_IMAGE_CODE_EXPIRES,text)

        #3,返回图片验证码
        return http.HttpResponse(image_data,content_type="image/png")

#2,发送短信验证码
class SmsCodeView(View):
    def get(self,request,mobile):
        #1,获取参数
        image_code = request.GET.get("image_code")
        image_code_id = request.GET.get("image_code_id")

        #2,校验参数
        #2,1 为空校验
        if not all([image_code,image_code_id]):
            return http.JsonResponse({"code":RET.PARAMERR,"errmsg":"参数不完整"})

        #2,2 获取redis中的图片验证码,校验为空
        redis_conn = get_redis_connection("code")
        pipeline = redis_conn.pipeline() #开启管道(事务)
        redis_image_code = redis_conn.get("img_code_%s"%image_code_id)

        #判断是否过期
        if not redis_image_code:
            return http.JsonResponse({"code": RET.NODATA, "errmsg": "图片验证码过期"})

        #删除redis验证码
        pipeline.delete("img_code_%s"%image_code_id)

        #2,3 图片验证码正确性
        if image_code.lower() != redis_image_code.decode().lower():
            return http.JsonResponse({"code": RET.DATAERR, "errmsg": "图片验证码错误"})

        #获取短信验证码标记
        send_flag = redis_conn.get("send_flag_%s"%mobile)
        if send_flag:
            return http.JsonResponse({"code":RET.DATAERR,"errmsg":"短信发送频繁"},status=400)

        #3,发送短信,并判断是否发送成功
        sms_code = "%06d"%random.randint(0,999999)
        print("sms_code = %s"%sms_code)
        # ccp = CCP()
        # result = ccp.send_template_sms(mobile, [sms_code, constants.REDIS_SMS_CODE_EXPIRES/60], 1)
        #
        # #判断是否发送成功
        # if result == -1:
        #     return http.JsonResponse({"code": RET.THIRDERR, "errmsg": "短信发送失败"})

        #使用celery发送短信
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code,constants.REDIS_SMS_CODE_EXPIRES/60)

        #测试短信发送
        # import time
        # time.sleep(10)

        #保存短信验证到redis
        pipeline.setex("sms_code_%s"%mobile,constants.REDIS_SMS_CODE_EXPIRES,sms_code)
        pipeline.setex("send_flag_%s"%mobile,60,True)

        pipeline.execute()#提交管道(事务)

        #4,返回响应
        return http.JsonResponse({"code":RET.OK,"errmsg":"ok"})
