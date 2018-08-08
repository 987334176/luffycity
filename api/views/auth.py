from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
class AuthView(ViewSetMixin,APIView):
    def login(self,request,*args,**kwargs):
        print('用户发POST请求来了',request)
        return Response({'code':1000})