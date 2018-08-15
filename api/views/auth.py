from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from api import models
from api.utils.response import BaseResponse
import uuid

class AuthView(ViewSetMixin,APIView):
    authentication_classes = []  # 空列表表示不认证

    def login(self,request,*args,**kwargs):
        """
        用户登陆认证
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        response = BaseResponse()  # 默认状态
        try:
            user = request.data.get('username')
            pwd = request.data.get('password')
            # 验证用户和密码
            obj = models.Account.objects.filter(username=user,password=pwd).first()
            if not obj:
                response.code = 10002
                response.error = '用户名或密码错误'
            else:
                uid = str(uuid.uuid4())  # 生成唯一id
                # 保存到数据库中,update_or_create表示更新或者创建
                # user=obj,这个是判断条件。当条件成立,更新token字段,值为uid
                # 当条件不成立时,增加一条记录。注意:增加时,有2个字段,分别是user和token
                models.UserToken.objects.update_or_create(user=obj, defaults={'token': uid})
                response.code = 99999
                response.data = uid

        except Exception as e:
            response.code = 10005
            response.error = '操作异常'

        return Response(response.dict)
