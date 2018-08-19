# import json
# from django.shortcuts import HttpResponse
# from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.versioning import URLPathVersioning
from rest_framework.pagination import PageNumberPagination

from api import models
from api.serializers.course import CourseModelSerializer, CourseThematicModelSerializer, CourseModuleModelSerializer, \
    CourseDetailModelSerializer,CourseFAQModelSerializer,CourseOutlineModelSerializer,CourseChapterModelSerializer
from api.utils.response import BaseResponse
from api.utils.serialization_general import SerializedData

class CoursesView(APIView):  # 所有课程,分页展示,每页1个

    def get(self, request, *args, **kwargs):
        # response = {'code':1000,'data':None,'error':None}
        queryset = models.Course.objects.all()
        serializer_class = CourseModelSerializer
        data = SerializedData(request,queryset,serializer_class).get_data()
        return Response(data)


class CourseDetailView(APIView):  # 课程详情
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(id=pk)
        serializer_class = CourseDetailModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)



class CourseThematicView(APIView):  # 所有的专题课
    def get(self, request, *args, **kwargs):
        queryset = models.Course.objects.all()
        serializer_class = CourseThematicModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)


class CourseModuleView(APIView):  # 具体id的学位课对应的所有模块名称
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(degree_course_id=pk)
        serializer_class = CourseModuleModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)


class CourseFAQView(APIView):  # 具体id的课程相关的所有常见问题
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(id=pk)
        serializer_class = CourseFAQModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)


class CourseOutlineView(APIView):  # 具体id课程相关的课程大纲
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(id=pk)
        serializer_class = CourseOutlineModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)


class CourseChapterView(APIView):  # 具体id课程相关的所有章节
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(id=pk)
        serializer_class = CourseChapterModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)

