from rest_framework import serializers
from api import models

# class DegreeCourseSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()


class DegreeCourseModelSerializer(serializers.ModelSerializer):  # 学位课所有信息
    class Meta:
        model = models.DegreeCourse
        fields = '__all__'

class DegreeCourseTeachersModelSerializer(serializers.ModelSerializer):  # 学位课的老师
    teachers = serializers.SerializerMethodField()

    class Meta:
        model = models.DegreeCourse
        fields = ['name','teachers']

    def get_teachers(self,row):
        teachers_list = row.teachers.all()
        return [ {'id':item.id,'name':item.name} for item in teachers_list]

class DegreeCourseScholarshipModelSerializer(serializers.ModelSerializer):  # 学位课的奖学金
    degreecourse_price_policy = serializers.SerializerMethodField()
    class Meta:
        model = models.DegreeCourse
        fields = ['name','degreecourse_price_policy']

    def get_degreecourse_price_policy(self,row):
        scholarships = row.scholarship_set.all()
        return [ {'id':item.id,'time_percent':item.time_percent,'value':item.value} for item in scholarships]