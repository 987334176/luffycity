#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import time
import random
import datetime
from django.conf import settings
from django.db import transaction
from django.db.models import F

from rest_framework.views import APIView
from rest_framework.response import Response

from api.utils.auth.token_auth import LuffyTokenAuthentication
from api.utils.auth.token_permission import LuffyPermission
from api.utils import redis_pool
from api.utils.alipay import AliPay

from repository import models


def generate_order_num():
    """
    生成订单编号, 且必须唯一
    :return:
    """
    while True:
        order_num = time.strftime('%Y%m%d%H%M%S', time.localtime()) + str(random.randint(111, 999))
        if not models.Order.objects.filter(order_number=order_num).exists():
            break
    return order_num


def generate_transaction_num():
    """
    生成流水编号, 且必须唯一
    :return:
    """
    while True:
        transaction_number = time.strftime('%Y%m%d%H%M%S', time.localtime()) + str(random.randint(111, 999))
        if not models.TransactionRecord.objects.filter(transaction_number=transaction_number).exists():
            break
    return transaction_number


class PayOrderView(APIView):
    authentication_classes = [LuffyTokenAuthentication, ]
    permission_classes = [LuffyPermission, ]

    def post(self, request, *args, **kwargs):
        """
        去支付，生成订单。
        获取前端提交的购买信息
            {
                course_price_list:[
                    {'policy_id':1, '':'course_id':1, 'coupon_record_id':1},
                    {'policy_id':2, '':'course_id':2, 'coupon_record_id':2},
                ],
                coupon_record_id:1,
                alipay: 99,
                balance: 1
            }

        1. 用户提交
            - balance
            - alipay
        2. 获取去结算列表

        课程
        3. 循环所有课程
            - 获取原价
            - 抵扣的钱




        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        response = {'code': 1000}
        try:
            """
            1. 获取用户提交数据
                - 获取支付金额
                - 获取贝里抵扣金额
            """
            policy_course_list = request.data.get('course_price_list')
            coupon_record_id = request.data.get('coupon_record_id')
            alipay = request.data.get('alipay')  # >= 0
            balance = request.data.get('balance')  # >= 0

            if balance > request.user.balance:
                raise Exception('账户中贝里余额不足')

            # 检查用户提交的信息在 redis结算列表 中是否存在，如果不存在，则需要用户从购物车中再次去结算
            payment_dict_bytes = redis_pool.conn.hget(settings.REDIS_PAYMENT_KEY, request.user.id)
            payment_dict = json.loads(payment_dict_bytes.decode('utf-8'))

            policy_course_dict = payment_dict['policy_course_dict']
            global_coupon_record_dict = payment_dict['global_coupon_record_dict']

            global_coupon_record = {}
            # 全局优惠券
            if coupon_record_id:
                if coupon_record_id not in global_coupon_record_dict:
                    raise Exception('全局优惠券在缓存中不存在')
                global_coupon_record = global_coupon_record_dict[coupon_record_id]

            # 当前时间
            current_date = datetime.datetime.now().date()
            current_datetime = datetime.datetime.now()

            # 原价
            total_price = 0
            # 总抵扣的钱
            discount = 0
            # 使用优惠券ID列表
            if coupon_record_id:
                use_coupon_record_id_list = [coupon_record_id, ]
            else:
                use_coupon_record_id_list = []
            # 课程和优惠券
            buy_course_record = []

            for cp in policy_course_list:
                _policy_id = cp['policy_id']
                _course_id = cp['course_id']
                _coupon_record_id = cp['coupon_record_id']

                temp = {
                    'course_id': _course_id,
                    'course_name': "course",
                    'valid_period': 0,  # 有效期：30
                    'period': 0,  # 有效期：一个月
                    'original_price': 0,
                    'price': 0,
                }
                if str(_course_id) not in policy_course_dict:
                    raise Exception('课程在缓存中不存在')

                redis_course = policy_course_dict[str(_course_id)]

                if str(_policy_id) != str(redis_course['policy_id']):
                    raise Exception('价格策略在缓存中不存在')

                # 课程是否已经下线或价格策略被修改
                policy_object = models.PricePolicy.objects.get(id=_policy_id)  # 价格策略对象
                course_object = policy_object.content_object  # 课程对象

                if course_object.id != _course_id:
                    raise Exception('课程和价格策略对应失败')
                if course_object.status != 0:
                    raise Exception('课程已下线，无法购买')

                # 选择的优惠券是否在缓存中
                redis_coupon_list = redis_course['coupon_record_list']
                redis_coupon_record = None
                for item in redis_coupon_list:
                    if item['id'] == _coupon_record_id:
                        redis_coupon_record = item
                        break
                if not redis_coupon_record:
                    raise Exception('单课程优惠券在缓存中不存在')

                # 计算购买原总价
                total_price += policy_object.price

                # 未使用单课程优惠券
                if redis_coupon_record['id'] == 0:
                    temp['price'] = policy_object.price
                    buy_course_record.append(temp)
                    continue

                temp['original_price'] = policy_object.price
                temp['valid_period'] = redis_coupon_record['policy_valid_period']
                temp['period'] = redis_coupon_record['policy_period']

                # 缓存中的优惠券是否已经过期
                begin_date = redis_coupon_record.get('begin_date')
                end_date = redis_coupon_record.get('end_date')
                if begin_date:
                    if current_date < begin_date:
                        raise Exception('优惠券使用还未到时间')
                if end_date:
                    if current_date > end_date:
                        raise Exception('优惠券已过期')

                # 使用的是单课程优惠券抵扣了多少钱；使用的 个人优惠券ID
                if redis_coupon_record['type'] == 0:
                    # 通用优惠券
                    money = redis_coupon_record['money_equivalent_value']
                    discount += money
                elif redis_coupon_record['type'] == 1:
                    # 满减券
                    money = redis_coupon_record['money_equivalent_value']
                    minimum_consume = redis_coupon_record['minimum_consume']
                    if policy_object.price >= minimum_consume:
                        discount += money
                elif redis_coupon_record['type'] == 2:
                    # 打折券
                    money = policy_object.price * redis_coupon_record['off_percent']
                    discount += money

                temp['price'] = policy_object.price - money
                buy_course_record.append(temp)
                use_coupon_record_id_list.append(redis_coupon_record['id'])

            # 全局优惠券
            print(global_coupon_record)
            begin_date = global_coupon_record.get('begin_date')
            end_date = global_coupon_record.get('end_date')
            if begin_date:
                if current_date < begin_date:
                    raise Exception('优惠券使用还未到时间')
            if end_date:
                if current_date > end_date:
                    raise Exception('优惠券已过期')

            # 使用全局优惠券抵扣了多少钱
            if global_coupon_record.get('type') == 0:
                # 通用优惠券
                money = global_coupon_record['money_equivalent_value']
                discount += money
            elif global_coupon_record.get('type') == 1:
                # 满减券
                money = global_coupon_record['money_equivalent_value']
                minimum_consume = global_coupon_record['minimum_consume']
                if (total_price - discount) >= minimum_consume:
                    discount += money
            elif global_coupon_record.get('type') == 2:
                # 打折券
                money = (total_price - discount) * global_coupon_record['off_percent']
                discount += money

            # 贝里抵扣的钱
            if balance:
                discount += balance

            if (alipay + discount) != total_price:
                raise Exception('总价、优惠券抵扣、贝里抵扣和实际支付的金额不符')

            # 创建订单 + 支付宝支付
            # 创建订单详细
            # 贝里抵扣 + 贝里记录
            # 优惠券状态更新
            actual_amount = 0
            if alipay:
                payment_type = 1  # 支付宝
                actual_amount = alipay
            elif balance:
                payment_type = 3  # 贝里
            else:
                payment_type = 2  # 优惠码

            with transaction.atomic():
                order_num = generate_order_num()
                if payment_type == 1:
                    order_object = models.Order.objects.create(
                        payment_type=payment_type,
                        order_number=order_num,
                        account=request.user,
                        actual_amount=actual_amount,
                        status=1,  # 待支付
                    )
                else:
                    order_object = models.Order.objects.create(
                        payment_type=payment_type,
                        order_number=order_num,
                        account=request.user,
                        actual_amount=actual_amount,
                        status=0,  # 支付成功，优惠券和贝里已够支付
                        pay_time=current_datetime
                    )

                for item in buy_course_record:
                    detail = models.OrderDetail.objects.create(
                        order=order_object,
                        content_object=models.Course.objects.get(id=item['course_id']),
                        original_price=item['original_price'],
                        price=item['price'],
                        valid_period_display=item['period'],
                        valid_period=item['valid_period']
                    )
                models.Account.objects.filter(id=request.user.id).update(balance=F('balance') - balance)
                models.TransactionRecord.objects.create(
                    account=request.user,
                    amount=request.user.balance,
                    balance=request.user.balance - balance,
                    transaction_type=1,
                    content_object=order_object,
                    transaction_number=generate_transaction_num()
                )
                effect_row = models.CouponRecord.objects.filter(id__in=use_coupon_record_id_list).update(
                    order=order_object,
                    used_time=current_datetime)

                if effect_row != len(use_coupon_record_id_list):
                    raise Exception('优惠券使用失败')

                response['payment_type'] = payment_type
                # 生成支付宝URL地址
                if payment_type == 1:
                    pay = AliPay(debug=True)
                    query_params = pay.direct_pay(
                        subject="路飞学城",  # 商品简单描述
                        out_trade_no=order_num,  # 商户订单号
                        total_amount=actual_amount,  # 交易金额(单位: 元 保留俩位小数)
                    )
                    pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)

                    response['pay_url'] = pay_url

        except IndentationError as e:
            response['code'] = 1001
            response['msg'] = str(e)

        return Response(response)
