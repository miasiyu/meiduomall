from celery_tasks.main import app
from django.core.mail import send_mail
from django.conf import settings

@app.task(bind=True,name="send_verify_url")
def send_verify_url(self,verify_url,email):

    #1,发送邮件
    try:
        result = send_mail(subject='美多商城,激活链接',
                  message=verify_url,
                  from_email=settings.EMAIL_FROM,
                  recipient_list=[email])
    except Exception as e:
        result = -1

    #2,判断短信是否发送成功
    if result == -1:
        print("发送失败!")
        #参数1: 重试的次数到了之后报错信息, 参数2: 隔几秒发一次,  参数3: 重新发送几次
        self.retry(exc=Exception("最终邮件没有发送成功"),countdown=5,max_retries=3)

