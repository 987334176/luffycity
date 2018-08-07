from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from api import models
from api import api_serializers  # 导入自定义的序列化



# Create your views here.
class CourseViewSet(ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = api_serializers.CourseSerializer