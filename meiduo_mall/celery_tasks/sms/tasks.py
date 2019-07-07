from celery_tasks.main import app
from meiduo_mall.libs.yuntongxun.sms import CCP

@app.task(bind=True,name="send_sms_code")
def send_sms_code(self,mobile,sms_code,time):

    #1,发送短信
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, time], 1)
    except Exception as e:
        result = -1

    #2,判断短信是否发送成功
    if result == -1:
        print("发送失败!")
        #参数1: 重试的次数到了之后报错信息, 参数2: 隔几秒发一次,  参数3: 重新发送几次
        self.retry(exc=Exception("最终没有发送成功"),countdown=5,max_retries=3)

