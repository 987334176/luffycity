from django.test import TestCase
import os
# Create your tests here.
'''
a. 查看所有学位课并打印学位课名称以及授课老师

b. 查看所有学位课并打印学位课名称以及学位课的奖学金

c. 展示所有的专题课 
    models.Course.objects.filter(degree_course__isnull=True)
    
d. 查看id=1的学位课对应的所有模块名称 

e. 获取id=1的专题课，并打印：课程名、级别(中文)、why_study、what_to_study_brief、所有recommend_courses

f. 获取id=1的专题课，并打印该课程相关的所有常见问题 

g. 获取id=1的专题课，并打印该课程相关的课程大纲

h. 获取id=1的专题课，并打印该课程相关的所有章节 

i. 获取id=1的专题课，并打印该课程相关的所有课时 
    第1章·Python 介绍、基础语法、流程控制
        01-课程介绍（一）
        01-课程介绍（一）
        01-课程介绍（一）
        01-课程介绍（一）
        01-课程介绍（一）
    第1章·Python 介绍、基础语法、流程控制
        01-课程介绍（一）
        01-课程介绍（一）
        01-课程介绍（一）
        01-课程介绍（一）
        01-课程介绍（一）
i.  获取id=1的专题课，并打印该课程相关的所有的价格策略 
'''
if __name__ == "__main__":
    # 设置django环境
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s11luffycity.settings")
    import django
    django.setup()

    from api import models

    # a.查看所有学位课并打印学位课名称以及授课老师
    # obj = models.DegreeCourse.objects.values("name", "teachers__name")
    # print(obj)
    #
    # b.查看所有学位课并打印学位课名称以及学位课的奖学金
    # obj = models.DegreeCourse.objects.all().values("name", "total_scholarship")
    # print(obj)
    #
    # c.展示所有的专题课
    # obj = models.Course.objects.filter(degree_course__isnull=True)
    # d.查看id = 1
    # 的学位课对应的所有模块名称
    # obj = models.Course.objects.filter(id=1).values("name", "degree_course")
    #
    # e.获取id = 1
    # 的专题课，并打印：课程名、级别(中文)、why_study、what_to_study_brief、所有recommend_courses
    # obj = models.Course.objects.filter(degree_course__isnull=True, id=1).values("name", "level",
    #                                                                             "coursedetail__why_study",
    #                                                                             "coursedetail__what_to_study_brief",
    #                                                                             "coursedetail__recommend_courses")
    #
    # f.获取id = 1
    # 的专题课，并打印该课程相关的所有常见问题
    # obj = models.Course.objects.filter(id=1)
    # for i in obj:
    #     print(i.asked_question.all())
    #
    # g.获取id = 1
    # 的专题课，并打印该课程相关的课程大纲
    # obj = models.CourseDetail.objects.filter(id=1).values("courseoutline__title")
    # print(obj)
    #
    # h.获取id = 1
    # 的专题课，并打印该课程相关的所有章节
    # obj = models.Course.objects.filter(id=1).values("coursechapters__name")
    # print(obj)
    #
    # i.获取id = 1
    # 的专题课，并打印该课程相关的所有的价格策略
    # obj = models.Course.objects.filter(id=1).values("coursechapters__name", "coursechapters__coursesections__name")
    #
    # print(obj)
    obj =models.Course.objects.get(id=1)
    chapter_list = obj.coursechapter_set.all()
    print(chapter_list)



