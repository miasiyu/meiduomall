from django.shortcuts import render
from django.views import View
from django import http
from meiduo_mall.utils.response_code import RET
from .models import Area
from django.core.cache import cache

#1,获取区域视图
class AreaView(View):
    def get(self,request):
        #1,获取参数
        area_id = request.GET.get("area_id")

        #2,校验参数,是否有area_id(如果有area_id表示获取市或者区,  如果没有获取省)
        if not area_id:
            #TODO 查询缓存
            province_list = cache.get("province_list")

            #如果有缓存数据直接返回
            if province_list:
                context = {
                    "code": RET.OK,
                    "province_list": province_list
                }
                return http.JsonResponse(context)

            #2,1 获取所有的省的数据
            provinces = Area.objects.filter(parent_id=None).all()

            #2,2 拼接数据
            province_list = []
            for province in provinces:
                province_list.append({
                    "id":province.id,
                    "name":province.name
                })
            context = {
                "code":RET.OK,
                "province_list":province_list
            }

            #TODO 缓存省的数据
            cache.set("province_list",province_list,3600*24*30)

            #2,3 返回响应
            return http.JsonResponse(context)
        else:

            #TODO 获取缓存市,区
            subs_list = cache.get("subs_%s"%area_id)

            #判断是否有缓存数据,如果有缓存数据直接返回
            if subs_list:
                context = {
                    "code": RET.OK,
                    "sub_data": {
                        "subs": subs_list
                    }
                }
                return http.JsonResponse(context)

            #3,1 获取市,区数据
            subs = Area.objects.filter(parent_id=area_id)

            #3,2 数据转换
            subs_list = []
            for sub in subs:
                subs_list.append({
                    "id":sub.id,
                    "name":sub.name
                })

            context = {
                "code":RET.OK,
                "sub_data":{
                    "subs":subs_list
                }

            }

            #TODO 缓存市,区
            cache.set("subs_%s"%area_id,subs_list,3600*24*30)

            #3,3 返回响应
            return http.JsonResponse(context)
