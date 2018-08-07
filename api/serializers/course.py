
from rest_framework import serializers
from api import models

# class CourseSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     name = serializers.CharField()


class CourseModelSerializer(serializers.ModelSerializer):  # 所有课程
    level_name = serializers.CharField(source='get_level_display')
    hours = serializers.CharField(source='coursedetail.hours')
    course_slogan = serializers.CharField(source='coursedetail.course_slogan')
    # recommend_courses = serializers.CharField(source='coursedetail.recommend_courses.all')

    recommend_courses = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id','name','level_name','hours','course_slogan','recommend_courses']

    def get_recommend_courses(self,row):
        recommend_list = row.coursedetail.recommend_courses.all()
        return [ {'id':item.id,'name':item.name} for item in recommend_list]

class CourseThematicModelSerializer(serializers.ModelSerializer):  # 所有的专题课
    class Meta:
        model = models.Course
        fields = '__all__'

class CourseModuleModelSerializer(serializers.ModelSerializer):  # 所有的专题课
    degree_course = serializers.CharField(source='degree_course.name')
    class Meta:
        model = models.Course
        fields = ['id','degree_course']

class CourseDetailModelSerializer(serializers.ModelSerializer):  # 具体id的学位课对应的所有模块名称
    level_name = serializers.CharField(source='get_level_display')
    why_study = serializers.CharField(source='coursedetail.why_study')
    what_to_study_brief = serializers.CharField(source='coursedetail.what_to_study_brief')

    recommend_courses = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id','name','level_name','why_study','what_to_study_brief','recommend_courses']

    def get_recommend_courses(self,row):
        recommend_list = row.coursedetail.recommend_courses.all()
        return [ {'id':item.id,'name':item.name} for item in recommend_list]

class CourseFAQModelSerializer(serializers.ModelSerializer):  # 具体id专题课程相关的所有常见问题
    asked_question = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id','name', 'asked_question']

    def get_asked_question(self, row):
        faq_list = row.asked_question.all()
        return [{'id': item.id, 'question': item.question, 'answer': item.answer} for item in faq_list]


class CourseOutlineModelSerializer(serializers.ModelSerializer):  # 具体id课程相关的课程大纲
    asked_question = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'name', 'asked_question']

    def get_asked_question(self, row):
        outline_list = row.coursedetail.courseoutline_set.all()
        return [{'id': item.id, 'title': item.title, 'content': item.content} for item in outline_list]

class CourseChapterModelSerializer(serializers.ModelSerializer):  # 具体id课程相关的所有章节
    chapter = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'name', 'chapter']

    def get_chapter(self, row):
        # print(row.__dict__,'11111111')
        chapter_list = row.coursechapter_set.all()
        # print(chapter_list)
        return [{'id': item.id, 'name': item.name} for item in chapter_list]
