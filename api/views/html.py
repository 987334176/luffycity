from django.shortcuts import render, HttpResponse, redirect
from api import models
from django_redis import get_redis_connection
import json

CONN = get_redis_connection("default")  # 使用redis连接池

def index(request):
    # print(request.session.get("user").username)
    return render(request,"index.html")

def login(request):
    return render(request,"login.html")

def logout(request):
    request.session.flush()  # 清理session
    return redirect('/login/')

def course(request):
    # print('course')
    print(request.session.get("token"))
    course_list = models.Course.objects.all()
    print(course_list)
    return render(request, "course.html",{'course_list':course_list})

def course_detail(request,pk):
    course = models.Course.objects.filter(id=pk).first()
    print(course.price_policy.all())
    return render(request, "course_detail.html", {'course': course})

def news(request):
    # print('news')
    return render(request, "news.html")

def shopping_cart(request):


    shopping_car_course_list = []

    # pattern = "shopping_car_%s_*" % (request.user.id,)
    pattern = "shopping_car_%s_%s" % (request.session.get('user').id, '*',)
    # print(pattern)

    user_key_list = CONN.keys(pattern)

    for key in user_key_list:
        list_1 = []
        price_policy_dict = json.loads(CONN.hget(key, 'price_policy_dict').decode('utf-8'))
        for sub in price_policy_dict:
            # print(i,type(i),'333333333333333')
            list_1.append(price_policy_dict.get(sub))

        temp = {
            'id': CONN.hget(key, 'id').decode('utf-8'),
            'name': CONN.hget(key, 'name').decode('utf-8'),
            'img': CONN.hget(key, 'img').decode('utf-8'),
            'default_price_id': CONN.hget(key, 'default_price_id').decode('utf-8'),
            'default_price': CONN.hget(key, 'default_price').decode('utf-8'),
            'price_policy_dict': list_1
        }
        # print("\r\n")

        # print('staend',a,type(a),'1111111111111')
        # print(a.get('valid_period'),'22222222222222')
        # print(price_policy_dict)
        for sub in price_policy_dict:
            # print(i,type(i),'333333333333333')
            temp['price_policy_list'] = price_policy_dict.get(sub)
            # print(price_policy_dict.get(sub).get('price'))
            # print(i,v)
            # for j in a.get(i):
            #     print(j)
        shopping_car_course_list.append(temp)


    print(shopping_car_course_list)
    return render(request, "shopping_cart.html",{'shopping_list':shopping_car_course_list})

