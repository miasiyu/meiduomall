from django.db import models

class Area(models.Model):
    name = models.CharField(max_length=20,verbose_name="区域名字")
    #related_name替换系统生成的area_set 的, 比如: 查询省下面所有的市,  或者市下面的区
    parent = models.ForeignKey('self',related_name="subs",on_delete=models.SET_NULL,null=True,blank=True,verbose_name="上级区域")

    class Meta:
        db_table = "tb_areas"

    def __str__(self):
        return self.name