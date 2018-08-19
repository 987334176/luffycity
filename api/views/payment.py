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


class CourseNotExistsException(Exception):
    def __init__(self, msg):
        self.msg = msg

class CouponType(object):
    def __init__(self,coupon_list,j_key):
        self.coupon_list = coupon_list
        self.j_key = j_key

    def get_coupon(self):
        coupon_dict = {}
        for j in range(1,len(self.coupon_list)+1):
            # print(len(self.coupon_list))
            for i in self.coupon_list:
                # print(i.coupon.coupon_type)
                if i.coupon.coupon_type == 0:  # 类型为立减
                    msg = '{}{}'.format(i.coupon.get_coupon_type_display(), i.coupon.money_equivalent_value)
                    # print(msg)
                    coupon_dict[j] = msg

                    # return msg
                elif i.coupon.coupon_type == 1:  # 类型为满减
                    msg = '满{}减{}'.format(i.coupon.minimum_consume, i.coupon.money_equivalent_value)
                    # print(msg)
                    coupon_dict[j] = msg
                    # return msg
                else:
                    msg = '{}折'.format(i.coupon.off_percent / 10)
                    # print(msg)
                    coupon_dict[j] = msg
                    # return msg

        CONN.hset(self.j_key, 'coupon_dict', coupon_dict)

        return coupon_dict

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
        response = BaseResponse()
        try:
            # 1.接受用户选择的要结算的课程ID列表
            userid = request.user.id
            print('用户id',userid)
            # [1,3,55]
            courseid_list = request.data.get('courseid')  # 拿到的是一个列表
            print('课程id',courseid_list)
            # 2.清空当前用户request.user.id结算中心的数据
            pattern = 'payment_%s_%s' % (userid, '*')
            # print(pattern)
            # 方式一：
            # key_list = CONN.keys(pattern)
            # CONN.delete(*key_list)
            # print(11)
            # 方式二：
            print(CONN.keys(pattern))
            for key in CONN.keys(pattern):
                # print()
                CONN.delete(key)  # 清空结算中心

            # 3.循环要加入结算中的所有课程ID列表

            import datetime
            today = datetime.date.today()
            # print(11)
            for course_id in courseid_list:
                shop_car_key = "shopping_car_%s_%s" % (userid, course_id)
                # print(shop_car_key)

                # 3.1 判断购物车中是否存在此key
                if not CONN.exists(shop_car_key):
                    raise CourseNotExistsException('购物车中不存在该课程')

                # 3.2 去购物车中获取课程信息
                id = CONN.hget(shop_car_key, 'id').decode('utf-8')
                name = CONN.hget(shop_car_key, 'name').decode('utf-8')
                img = CONN.hget(shop_car_key, 'img').decode('utf-8')
                default_price_id = CONN.hget(shop_car_key, 'default_price_id').decode('utf-8')

                price_policy_dict = json.loads(CONN.hget(shop_car_key, 'price_policy_dict').decode('utf-8'))
                price_policy = price_policy_dict[default_price_id]
                valid_period = price_policy_dict[default_price_id].get('valid_period_display')
                """
                {
                    'id':1,
                    'price':99.99,
                    'valid_period':60,
                    'valid_period_display':2个月
                }
                """

                # 3.3 根据课程ID获取该课程可用的优惠券

                coupon_list = models.CouponRecord.objects.filter(account_id=userid,
                                                                 status=0,
                                                                 coupon__valid_begin_date__lte=today,
                                                                 coupon__valid_end_date__gte=today,
                                                                 coupon__object_id=course_id,
                                                                 coupon__content_type__model='course'
                                                                 )
                # for i in coupon_list:
                #     # print(i.coupon.coupon_type)
                #     if i.coupon.coupon_type == 0:  # 类型为立减
                #         print('{}{}'.format(i.coupon.get_coupon_type_display(), i.coupon.money_equivalent_value))
                #     elif i.coupon.coupon_type == 1:  # 类型为满减
                #         print('满{}减{}'.format(i.coupon.minimum_consume, i.coupon.money_equivalent_value))
                #     else:
                #         print('{}折'.format(i.coupon.off_percent/10))

                # 加入结算中心
                # 加入结算中心redis
                j_key = "payment_%s_%s" % (userid, id,)

                CONN.hset(j_key, 'id', course_id)
                CONN.hset(j_key, 'name', name)
                CONN.hset(j_key, 'img', img)
                CONN.hset(j_key, 'price_id', default_price_id)
                CONN.hset(j_key, 'price', price_policy_dict[default_price_id].get('price'))
                CONN.hset(j_key, 'valid_period', valid_period)
                CONN.hset(j_key, 'discount_price', price_policy_dict[default_price_id].get('price'))
                CONN.hset(j_key, 'price_policy', price_policy)

                CouponType(coupon_list,j_key).get_coupon()  # 将优惠券加入到redis中
                # print(11)

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

            # 4.获取当前用户所有未绑定课程优惠券
            #       - 未使用
            #       - 有效期内
            #       - 加入结算中心：glocal_coupon_用户ID

            global_coupon_list = models.CouponRecord.objects.filter(account_id=userid,
                                                                    status=0,
                                                                    coupon__valid_begin_date__lte=today,
                                                                    coupon__valid_end_date__gte=today,
                                                                    coupon__content_type__isnull=True
                                                                    )
            # 加入到结算中心
            # print(global_coupon_list)
            j_key = "glocal_coupon_%s" % (userid,)
            CouponType(global_coupon_list, j_key).get_coupon()  # 将优惠券加入到redis中
            # print(11)


        except CourseNotExistsException as e:
            response.code = 1010
            response.error = e.msg

        except Exception as e:
            print(e)

        return Response('...')

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



