from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.response import Response
from api import models
import json

SHOPPING_CAR = {}
# SHOPPING_CAR = {
#     1:{
#         2:{
#             'title':'xxxx',
#             'price':1,
#             'price_list':[
#                 {'id':11,},
#                 {'id':22},
#                 {'id':33},
#             ]
#         },
#         3:{},
#         5:{}
#     },
#     2:{},
#     3:{},
# }

class ShoppingCartView(ViewSetMixin,APIView):

    def create(self,request,*args,**kwargs):
        """
        加入购物车
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        """
        1. 接受用户选中的课程ID和价格策略ID
        2. 判断合法性
            - 课程是否存在？
            - 价格策略是否合法？
        3. 把商品和价格策略信息放入购物车 SHOPPING_CAR
        
        注意：用户ID=1
        """
        # c_obj = Course.objects.filter(id=1).first()
        # print(c_obj.price_policy.all())
        ret = {'code': 1000}
        try:
            now_course = models.Course.objects.filter(id=1).first()  # 当前课程
            price_policy = now_course.price_policy.all()  # 当前课程所有价格策略
            # print(price_policy)
            price_id_list = []
            for i in price_policy:
                # print(i.id)
                price_id_list.append(i.id)

            # print(request.body)
            data = (request.body).decode('utf-8')

            data_dict = json.loads(data)

            card_id = data_dict.get("picked")
            # print(price_id_list)
            # print(card_id)
            if card_id in price_id_list:
                card_depot = models.PricePolicy.objects.filter(id=card_id).first()  # 当前购物车价格策略
                SHOPPING_CAR[1] = {1: {'title': now_course.name, 'price': card_depot.price, 'price_list': price_id_list}}

            else:
                ret['code'] = 403
                ret['errot'] = '非法请求'

        except Exception as e:
            # print(e)
            ret.code = 500
            ret.error = '获取数据失败'

        print(SHOPPING_CAR)
        print(json.dumps(SHOPPING_CAR))
        return Response(ret)