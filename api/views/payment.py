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

CONN = get_redis_connection("default")  # 使用redis连接池


class PaymentView(ViewSetMixin, APIView):
    authentication_classes = [LuffyAuthentication, ]

    def create(self, request, *args, **kwargs):
        """
        在结算中添加课程
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 1.接收用户选择的要结算的课程ID列表
        choice_list = request.data.get('course_id')
        # print(choice_list)

        # 2.清空当前用户request.user.id结算中心的数据
        #   key = payment_1*
        CONN.delete('payment_1*')

        # 3.循环要加入结算中的所有课程ID列表

        """
        for course_id in 用户提交课程ID列表:
            3.1 根据course_id,request.user.id去购物车中获取商品信息：商品名称、图片、价格（id,周期,显示周期,价格）
            3.2 根据course_id,request.user.id获取 
                    - 当前用户
                    - 当前课程
                    - 可用的优惠券

            加入结算中心

            提示：可以使用contenttypes
        """
        '''
        # 2.1 课程是否存在？
        temp = {
                    'id': CONN.hget(key, 'id').decode('utf-8'),
                    'name': CONN.hget(key, 'name').decode('utf-8'),
                    'img':CONN.hget(key, 'img').decode('utf-8'),
                    'default_price_id':CONN.hget(key, 'default_price_id').decode('utf-8'),
                    'price_policy_dict': json.loads(CONN.hget(key, 'price_policy_dict').decode('utf-8'))
                }
        '''
        user_id = request.user.id
        print('用户id', user_id)

        # 从购物车中获取数据
        pattern = "shopping_car_%s_%s" % (request.user.id, '*',)
        # print(pattern)
        user_key_list = CONN.keys(pattern)

        for course_id in choice_list:  # 用户选择的要结算的课程ID列表
            for key in user_key_list:  # 当前用户购物车列表
                id = CONN.hget(key, 'id').decode('utf-8')  # 获取购物车课程id
                if id == course_id:  # 判断用户选择课程id和购物车课程id相等
                    name = CONN.hget(key, 'name').decode('utf-8')  # 课程名
                    default_price_id = CONN.hget(key, 'default_price_id').decode('utf-8')  # 默认价格策略id
                    # 所有价格策略
                    price_policy_dict = json.loads(CONN.hget(key, 'price_policy_dict').decode('utf-8'))

                    print('课程id',id)
                    print('课程名',name)
                    print('默认价格策略',default_price_id)
                    valid_period = price_policy_dict[default_price_id].get('valid_period_display')
                    print('有效期', valid_period)
                    print('原价',price_policy_dict[default_price_id].get('price'))
                    print('折后价', price_policy_dict[default_price_id].get('price'))
                    print('所有价格策略',price_policy_dict)

                    # 加入结算中心redis
                    j_key = "payment_%s_%s" % (user_id, id,)

                    CONN.hset(j_key, 'id', course_id)
                    CONN.hset(j_key, 'name', name)
                    CONN.hset(j_key, 'price_id', default_price_id)
                    CONN.hset(j_key, 'price', price_policy_dict[default_price_id].get('price'))
                    CONN.hset(j_key, 'valid_period', valid_period)
                    CONN.hset(j_key, 'discount_price', price_policy_dict[default_price_id].get('price'))

                    # 查询当前课程的 绑定课程优惠券
                    obj1 = models.Course.objects.filter(id=id).first()
                    if obj1.coupon.all():  # 反向查询该课程的所有优惠券
                        print("绑定课程优惠券#########################")
                        for i in obj1.coupon.all():  # 循环每一个优惠券
                            print('绑定课程优惠券个数',len(obj1.coupon.all()))
                            coupon_dict = {}  # 空字典
                            for j in range(len(obj1.coupon.all())):  # for循环长度
                                if i.coupon_type == 0:  # 类型为立减
                                    coupon_dict[j] = '{}{}'.format(i.get_coupon_type_display(), i.money_equivalent_value)
                                    # 增加到redis中
                                    CONN.hset(j_key, 'coupon_dict', coupon_dict)
                                    # print(111)
                                    print(
                                        '{}{}'.format(i.get_coupon_type_display(), i.money_equivalent_value))
                                elif i.coupon_type == 1:
                                    coupon_dict[j] = '满{}减{}'.format(i.minimum_consume, i.money_equivalent_value)
                                    CONN.hset(j_key, 'coupon_dict', coupon_dict)
                                    print('满{}减{}'.format(i.minimum_consume, i.money_equivalent_value))
                                else:
                                    # print(i.id)
                                    coupon_dict[j] = '{}折'.format(i.off_percent)
                                    CONN.hset(j_key, 'coupon_dict', coupon_dict)
                                    print('{}折'.format(i.off_percent))


        # 绑定课程的优惠券


        # obj = models.CouponRecord.objects.filter(account=user_id, coupon__object_id__isnull=False)
        # print('绑定课程优惠券#################')
        # if obj:
        #     for i in obj:
        #         if i.coupon.coupon_type == 0:
        #             print('{}{}'.format(i.coupon.get_coupon_type_display(), i.coupon.money_equivalent_value))
        #         elif i.coupon.coupon_type == 1:
        #             print('满{}减{}'.format(i.coupon.minimum_consume, i.coupon.money_equivalent_value))
        #         else:
        #             # print(i.coupon.id)
        #             print('{}折'.format(i.coupon.off_percent))


        # 4.获取当前用户所有未绑定课程优惠券
        #       - 未使用
        #       - 有效期内
        #       - 加入结算中心：glocal_coupon_用户ID

        # 当前用户未绑定课程的优惠券
        obj2 = models.CouponRecord.objects.filter(account=user_id, coupon__object_id__isnull=True)
        print('未绑定课程优惠券#################')
        if obj2:
            # 通用优惠券redis key
            coupon_key = "general_coupon_%s" % (user_id)
            for i in obj2:
                general_coupon_dict = {}  # 空字典
                print('未绑定课程优惠券个数 %s' % (len(obj2)))
                for j in range(len(obj2)):
                    if i.coupon.coupon_type == 0:  # 类型为立减
                        general_coupon_dict[j] = '{}{}'.format(i.coupon.get_coupon_type_display(), i.coupon.money_equivalent_value)
                        CONN.hset(coupon_key, 'coupon_dict', general_coupon_dict)
                        print('{}{}'.format(i.coupon.get_coupon_type_display(), i.coupon.money_equivalent_value))
                    elif i.coupon.coupon_type == 1:
                        general_coupon_dict[j] = '满{}减{}'.format(i.coupon.minimum_consume, i.coupon.money_equivalent_value)
                        CONN.hset(coupon_key, 'coupon_dict', general_coupon_dict)
                        print('满{}减{}'.format(i.coupon.minimum_consume, i.coupon.money_equivalent_value))
                    else:
                        general_coupon_dict[j] = '{}折'.format(i.coupon.off_percent)
                        CONN.hset(coupon_key, 'coupon_dict', general_coupon_dict)
                        print('{}折'.format(i.coupon.off_percent))


        return Response('ok')

    def list(self, request, *args, **kwargs):
        """
        查看结算中心
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        # 1. 根据用户ID去结算中心获取该用户所有要结算课程
        course_id = request.query_params.get('course_id')
        print('课程id',course_id)
        obj = models.Course.objects.filter(id=course_id).first()
        print('结算课程',obj.name)
        # 2. 根据用户ID去结算中心获取该用户所有可用未绑定课程的优惠券
        user_id =request.user.id
        print('用户id', user_id)
        obj2 = models.CouponRecord.objects.filter(account=user_id, coupon__object_id__isnull=True)
        if obj2:
            for i in obj2:
                if i.coupon.coupon_type == 0:
                    print('{}{}'.format(i.coupon.get_coupon_type_display(), i.coupon.money_equivalent_value))
                elif i.coupon.coupon_type == 1:
                    print('满{}减{}'.format(i.coupon.minimum_consume, i.coupon.money_equivalent_value))
                else:
                    print(i.coupon.id)
                    print('{}折'.format(i.coupon.off_percent))

        # 3. 用户表中获取贝里余额
        beili = models.Account.objects.filter(id=user_id).first()
        print('用户贝里',beili.balance)

        # 4. 以上数据构造成一个字典

        return Response('...')

    def update(self, request, *args, **kwargs):
        """
        更新优惠券
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 1. 获取用户提交：
        #       course_id=1,coupon_id=3
        #       course_id=0,coupon_id=6

        # 2. course_id=1 --> 去结算中心获取当前用户所拥有的绑定当前课程优惠，并进行校验
        #       - 成功：defaul_coupon_id=3
        #       - 否则：非法请求

        # 3. course_id=0 --> 去结算中心获取当前用户所拥有的未绑定课程优惠，并进行校验
        #       - 成功：defaul_coupon_id=3
        #       - 否则：非法请求



