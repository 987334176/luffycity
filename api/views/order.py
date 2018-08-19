import json
import redis
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.response import Response
from api.utils.auth import LuffyAuthentication
from api import models
from api.utils.response import BaseResponse

from django_redis import get_redis_connection

CONN = get_redis_connection("default")

"""
{
    payment_2_1:{
        id:1,
        name:'Python基础',
        img:'xxx',
        price:99.99,
        period:90,
        period_display:3个月,
        default_coupon_id:0,
        coupon_dict:{
            '1':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
            '2':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
            '3':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
        }
    },
    payment_2_3:{
        id:2,
        name:'Python进阶',
        img:'xxx',
        price:99.99,
        period:90,
        period_display:3个月,
        default_coupon_id:0,
        coupon_dict:{
            '1':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
            '2':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
            '3':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
        }
    },
    global_coupon_2:{
        '1':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
            '2':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
            '3':{'type':0,'text':'立减','money_equivalent_value':'xx','off_percent':'xx','minimum_consume'},
    }
}


"""


class OrderView(ViewSetMixin, APIView):
    authentication_classes = [LuffyAuthentication, ]

    def create(self, request, *args, **kwargs):
        """
        立即支付
        :param args:
        :param kwargs:
        :return:
        """
        response = BaseResponse()

        try:
            # 1. 接收用户发送的数据
            """
            {'balance':1000,'alipay':228 }
            """
            balance = request.data.get('balance')  # 贝里
            # print(balance)
            if balance.isdigit():
                balance = int(balance)
            else:
                return Response('贝里非法')

            alipay = request.data.get('alipay')  # 支付金额
            print(balance,alipay)

            # 2. 检验贝里余额是否够用
            # print(request.user.balance)
            # print(request.user.balance < balance)

            # print(type(request.user.balance),type(balance))
            # print(request.user.balance < balance)
            if request.user.balance < balance:
                return Response('贝里余额不足')

            # 3.获取结算中心的每个课程信息并应用优惠券
            #3.1 获取当前用户结算中心的所有key
            key = "payment_%s*" % request.user.id
            key_list = CONN.keys(key)
            # print(key_list)
            total_price = 0
            discount = 0

            coupon_id_list = []

            course_dict = {}
            #3.2 根据key获取结算中心的课程
            for key in key_list:
                # print(11)
                id = CONN.hget(key, 'id').decode('utf-8')
                print(id)
                name = CONN.hget(key, 'name').decode('utf-8')
                print(name)
                img = CONN.hget(key, 'img').decode('utf-8')
                print(img)
                price_id = CONN.hget(key, 'price_id').decode('utf-8')
                print(price_id)
                price = CONN.hget(key, 'price').decode('utf-8')
                print(price)
                valid_period = CONN.hget(key, 'valid_period').decode('utf-8')
                print(valid_period)
                # period_display = CONN.hget(key, 'period_display').decode('utf-8')
                # print(period_display)
                # default_coupon_id = CONN.hget(key, 'default_coupon_id').decode('utf-8')
                # print(default_coupon_id)
                # discount_price = CONN.hget(key, 'discount_price').decode('utf-8')
                # print(discount_price)
                # coupon_dict = json.loads(CONN.hget(key, 'coupon_dict').decode('utf-8'))
                # print(coupon_dict)
                # print(1111)
                # print(price,type(price))
                price = float(price)
                # print(1111)
                # 3.3 计算总原价
                # print(price)
                total_price += price
                # print(total_price)
                print(total_price,'总价')

                if default_coupon_id == 0:
                    # 未使用
                    discount += 0
                else:
                    pass
                    # # 使用优惠券
                    # if coupon_dict['type'] == 0:
                    #     discount += price if coupon_dict['money_equivalent_value'] > price else coupon_dict[
                    #         'money_equivalent_value']
                    # elif coupon_dict['type'] == 1:
                    #     pass
                    # elif coupon_dict['type'] == 2:
                    #     discount += price * （100 - 折扣） / 100
                    #
                    # coupon_id_list.append(default_coupon_id)

            """
                3.1 获取当前用户结算中心的所有key
                    key = "payment_%s*" %request.user.id
                    key_list = CONN.keys(key)


                total_price = 0
                discount = 0

                coupon_id_list = []

                course_dict = {}

                3.2 根据key获取结算中心的课程
                    for key in key_list:
                        id = CONN.hget(key,'id').decode('utf-8')
                        name = CONN.hget(key,'name').decode('utf-8')
                        img = CONN.hget(key,'img').decode('utf-8')
                        price = CONN.hget(key,'price').decode('utf-8')
                        period = CONN.hget(key,'period').decode('utf-8')
                        period_display = CONN.hget(key,'period_display').decode('utf-8')
                        default_coupon_id = CONN.hget(key,'default_coupon_id').decode('utf-8')
                        coupon_dict = json.loads(CONN.hget(key,'coupon_dict').decode('utf-8'))

                        # 3.3 计算总原价
                        total_price += price
                        # 3.4 计算要抵扣的价格
                        if default_coupon_id == 0:
                            # 未使用
                            discount += 0
                        else:
                            # 使用优惠券
                            if coupon_dict['type'] == 0:    
                                discount += price if coupon_dict['money_equivalent_value'] > price else coupon_dict['money_equivalent_value']
                            elif coupon_dict['type'] == 1:
                                pass 
                            elif coupon_dict['type'] == 2:
                                discount += price * （100-折扣）/ 100

                            coupon_id_list.append(default_coupon_id)

                        # 封装字典,用于订单插入
                        course_dict[id] = {
                            id = CONN.hget(key,'id').decode()
                            name = CONN.hget(key,'name').decode()
                            price = CONN.hget(key,'price').decode()
                            period = CONN.hget(key,'period').decode()
                            default_coupon_id = CONN.hget(key,'default_coupon_id').decode(),
                            price:999,
                            discount:99,

                        }

                3

            """

            # 4.处理未绑定课程的优惠券
            """
                4.1 去redis中获取 global_coupon_2

                    default_coupon_id = CONN.hget('global_coupon_2','default_coupon_id')
                    coupon_dict = CONN.hget('global_coupon_2','coupon_dict')

                4.2 判断是否使用优惠券
                    if default_coupon_id == 0:
                        pass
                    else:
                         # 使用优惠券
                            if coupon_dict['type'] == 0:    
                                discount += price if coupon_dict['money_equivalent_value'] > price else coupon_dict['money_equivalent_value']
                            elif coupon_dict['type'] == 1:
                                pass 
                            elif coupon_dict['type'] == 2:
                                discount += price * （100-折扣）/ 100

                            coupon_id_list.append(default_coupon_id)

            """

            # 5. 判断是否：total_price-discount-balance/10 = alipay
            # total_price = 0
            # discount = 0
            # balance
            # alipay
            # raise Exception('价格对不上')

            # 6. 生成订单
            """
            with transcation.atomic():
                6.1  obj = models.Order.objects.create(...)

                6.2  创建多个订单详细
                    for k,v in course_dict.items():
                        detail = OrderDetail.objects.create(order=obj)
                                 EnrolledCourse.objects.create(..,order_detail=detail)

                6.3 更新优惠券
                    count = models.CouponRecord.objects.filter(id__in=coupon_id_list).update(status=2)
                    if count != len(coupon_id_list):
                         报错..

                6.4 更新贝里余额
                    models.account.objects.filter(id=request.user.id).update(balance=F('balance')-balance)

                6.5 创建贝里转账记录
                    models.TransactionRecord.objects.create(,,balance)

            """

            # 7. 生成去支付宝支付的连接


        except Exception as e:
            print(e)
            pass

        return Response('ok')