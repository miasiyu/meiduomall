from django.db import models
from meiduo_mall.utils.models import BaseModel

class OAuthQQUser(BaseModel):
    #1,关联用户模型类, models.CASCADE,删除主表(user)的时候, 该条数据也删除
    user = models.ForeignKey('users.User',on_delete=models.CASCADE,verbose_name="关联的用户")
    openid = models.CharField(max_length=64,verbose_name="qq用户的标识")

    class Meta:
        db_table = "tb_oauth_user"


