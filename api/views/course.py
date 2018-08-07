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


# class SerializedData(object):
#     def __init__(self,request,queryset,serializer_class):
#         self.request = request
#         self.queryset = queryset
#         self.serializer_class = serializer_class
#
#
#     def get_data(self):
#         ret = BaseResponse()
#         try:
#             # 从数据库获取数据
#             queryset = self.queryset.order_by('id')
#
#             # 分页
#             page = PageNumberPagination()
#             course_list = page.paginate_queryset(queryset, self.request, self)
#
#             # 分页之后的结果执行序列化
#             ser = self.serializer_class(instance=course_list, many=True)
#
#             ret.data = ser.data
#         except Exception as e:
#             ret.code = 500
#             ret.error = '获取数据失败'
#
#         return ret.dict



class CoursesView(APIView):  # 所有课程,分页展示,每页1个

    def get(self, request, *args, **kwargs):
        # response = {'code':1000,'data':None,'error':None}
        queryset = models.Course.objects.all()
        serializer_class = CourseModelSerializer
        data = SerializedData(request,queryset,serializer_class).get_data()
        return Response(data)
        # ret = BaseResponse()
        # try:
        #     # 从数据库获取数据
        #     queryset = models.Course.objects.all()
        #
        #     # 分页
        #     page = PageNumberPagination()
        #     course_list = page.paginate_queryset(queryset, request, self)
        #
        #     # 分页之后的结果执行序列化
        #     ser = CourseModelSerializer(instance=course_list, many=True)
        #
        #     ret.data = ser.data
        # except Exception as e:
        #     ret.code = 500
        #     ret.error = '获取数据失败'
        #
        # return Response(ret.dict)


class CourseDetailView(APIView):  # 课程详情
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(id=pk)
        serializer_class = CourseDetailModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)
        # response = {'code': 1000, 'data': None, 'error': None}
        # try:
        #     course = models.Course.objects.get(id=pk)
        #     ser = CourseDetailModelSerializer(instance=course)
        #     response['data'] = ser.data
        # except Exception as e:
        #     response['code'] = 500
        #     response['error'] = '获取数据失败'
        # return Response(response)



class CourseThematicView(APIView):  # 所有的专题课
    def get(self, request, *args, **kwargs):
        queryset = models.Course.objects.all()
        serializer_class = CourseThematicModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)
        # response = {'code':1000,'data':None,'error':None}
        # ret = BaseResponse()
        # try:
        #     # 从数据库获取数据
        #     queryset = models.Course.objects.get_queryset().order_by('id')
        #
        #     # 分页
        #     page = PageNumberPagination()
        #     course_list = page.paginate_queryset(queryset, request, self)
        #
        #     # 分页之后的结果执行序列化
        #     ser = CourseThematicModelSerializer(instance=course_list, many=True)
        #
        #     ret.data = ser.data
        # except Exception as e:
        #     ret.code = 500
        #     ret.error = '获取数据失败'
        #
        # return Response(ret.dict)


class CourseModuleView(APIView):  # 具体id的学位课对应的所有模块名称
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(degree_course_id=pk)
        serializer_class = CourseModuleModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)
        # ret = BaseResponse()
        # try:
        #     # 从数据库获取数据
        #     # 防止出现UnorderedObjectListWarning: Pagination may yield...
        #     queryset = models.Course.objects.filter(degree_course_id=pk).order_by('id')
        #     print(queryset)
        #     # 分页
        #     page = PageNumberPagination()
        #     course_list = page.paginate_queryset(queryset, request, self)
        #
        #     # 分页之后的结果执行序列化
        #     ser = CourseModuleModelSerializer(instance=course_list, many=True)
        #     print(ser.data)
        #
        #     ret.data = ser.data
        # except Exception as e:
        #     ret.code = 500
        #     ret.error = '获取数据失败'
        #
        # return Response(ret.dict)

class CourseFAQView(APIView):  # 具体id的课程相关的所有常见问题
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(id=pk)
        serializer_class = CourseFAQModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)
        # ret = BaseResponse()
        # try:
        #     # 从数据库获取数据
        #     # 防止出现UnorderedObjectListWarning: Pagination may yield...
        #     queryset = models.Course.objects.filter(id=pk).order_by('id')
        #     print(queryset)
        #     # 分页
        #     page = PageNumberPagination()
        #     course_list = page.paginate_queryset(queryset, request, self)
        #
        #     # 分页之后的结果执行序列化
        #     ser = CourseFAQModelSerializer(instance=course_list, many=True)
        #     print(ser.data)
        #
        #     ret.data = ser.data
        # except Exception as e:
        #     ret.code = 500
        #     ret.error = '获取数据失败'
        #
        # return Response(ret.dict)

class CourseOutlineView(APIView):  # 具体id课程相关的课程大纲
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(id=pk)
        serializer_class = CourseOutlineModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)
        # ret = BaseResponse()
        # try:
        #     # 从数据库获取数据
        #     # 防止出现UnorderedObjectListWarning: Pagination may yield...
        #     queryset = models.Course.objects.filter(id=pk).order_by('id')
        #     print(queryset)
        #     # 分页
        #     page = PageNumberPagination()
        #     course_list = page.paginate_queryset(queryset, request, self)
        #
        #     # 分页之后的结果执行序列化
        #     ser = CourseOutlineModelSerializer(instance=course_list, many=True)
        #     print(ser.data)
        #
        #     ret.data = ser.data
        # except Exception as e:
        #     ret.code = 500
        #     ret.error = '获取数据失败'
        #
        # return Response(ret.dict)


class CourseChapterView(APIView):  # 具体id课程相关的所有章节
    def get(self, request, pk, *args, **kwargs):
        queryset = models.Course.objects.filter(id=pk)
        serializer_class = CourseChapterModelSerializer
        data = SerializedData(request, queryset, serializer_class).get_data()
        return Response(data)
        # ret = BaseResponse()
        # try:
        #     # 从数据库获取数据
        #     # 防止出现UnorderedObjectListWarning: Pagination may yield...
        #     queryset = models.Course.objects.filter(id=pk).order_by('id')
        #     # 分页
        #     page = PageNumberPagination()
        #     course_list = page.paginate_queryset(queryset, request, self)
        #
        #     # 分页之后的结果执行序列化
        #     ser = CourseChapterModelSerializer(instance=course_list, many=True)
        #     # print(ser.data)
        #
        #     ret.data = ser.data
        # except Exception as e:
        #     # print(e)
        #     ret.code = 500
        #     ret.error = '获取数据失败'
        #
        # return Response(ret.dict)