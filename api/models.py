from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.db import models
import hashlib


# ######################## 课程相关 ########################

class CourseCategory(models.Model):
    """课程大类, e.g 前端  后端..."""
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "01.课程大类"


class CourseSubCategory(models.Model):
    """课程子类, e.g python linux """
    category = models.ForeignKey("CourseCategory")
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "02.课程子类"


class DegreeCourse(models.Model):
    """学位课程"""
    name = models.CharField(max_length=128, unique=True)
    course_img = models.CharField(max_length=255, verbose_name="缩略图")
    brief = models.TextField(verbose_name="学位课程简介", )
    total_scholarship = models.PositiveIntegerField(verbose_name="总奖学金(贝里)", default=40000)  # 2000 2000
    mentor_compensation_bonus = models.PositiveIntegerField(verbose_name="本课程的导师辅导费用(贝里)", default=15000)
    period = models.PositiveIntegerField(verbose_name="建议学习周期(days)", default=150)  # 为了计算学位奖学金
    prerequisite = models.TextField(verbose_name="课程先修要求", max_length=1024)
    teachers = models.ManyToManyField("Teacher", verbose_name="课程讲师")

    # 用于GenericForeignKey反向查询， 不会生成表字段，切勿删除
    # coupon = GenericRelation("Coupon")

    # 用于GenericForeignKey反向查询，不会生成表字段，切勿删除
    degreecourse_price_policy = GenericRelation("PricePolicy")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "03.学位课"


class Teacher(models.Model):
    """讲师、导师表"""
    name = models.CharField(max_length=32)
    role_choices = ((0, '讲师'), (1, '导师'))
    role = models.SmallIntegerField(choices=role_choices, default=0)
    title = models.CharField(max_length=64, verbose_name="职位、职称")
    signature = models.CharField(max_length=255, help_text="导师签名", blank=True, null=True)
    image = models.CharField(max_length=128)
    brief = models.TextField(max_length=1024)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "04.导师或讲师"


class Scholarship(models.Model):
    """学位课程奖学金"""
    degree_course = models.ForeignKey("DegreeCourse")
    time_percent = models.PositiveSmallIntegerField(verbose_name="奖励档位(时间百分比)", help_text="只填百分值，如80,代表80%")
    value = models.PositiveIntegerField(verbose_name="奖学金数额")

    def __str__(self):
        return "%s:%s" % (self.degree_course, self.value)

    class Meta:
        verbose_name_plural = "05.学位课奖学金"


class Course(models.Model):
    """专题课/学位课模块表"""
    name = models.CharField(max_length=128, unique=True)
    course_img = models.CharField(max_length=255)
    sub_category = models.ForeignKey("CourseSubCategory")
    course_type_choices = ((0, '付费'), (1, 'VIP专享'), (2, '学位课程'))
    course_type = models.SmallIntegerField(choices=course_type_choices)

    # 不为空；学位课的某个模块
    # 为空；专题课
    degree_course = models.ForeignKey("DegreeCourse", blank=True, null=True, help_text="若是学位课程，此处关联学位表")

    brief = models.TextField(verbose_name="课程概述", max_length=2048)
    level_choices = ((0, '初级'), (1, '中级'), (2, '高级'))
    level = models.SmallIntegerField(choices=level_choices, default=1)
    pub_date = models.DateField(verbose_name="发布日期", blank=True, null=True)
    period = models.PositiveIntegerField(verbose_name="建议学习周期(days)", default=7)  #
    order = models.IntegerField("课程顺序", help_text="从上一个课程数字往后排")
    attachment_path = models.CharField(max_length=128, verbose_name="课件路径", blank=True, null=True)
    status_choices = ((0, '上线'), (1, '下线'), (2, '预上线'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    template_id = models.SmallIntegerField("前端模板id", default=1)

    # coupon = GenericRelation("Coupon")

    # 用于GenericForeignKey反向查询，不会生成表字段，切勿删除
    price_policy = GenericRelation("PricePolicy")

    asked_question = GenericRelation("OftenAskedQuestion")


    def __str__(self):
        return "%s(%s)" % (self.name, self.get_course_type_display())


    def save(self, *args, **kwargs):
        if self.course_type == 2:
            if not self.degree_course:
                raise ValueError("学位课程必须关联对应的学位表")
        super(Course, self).save(*args, **kwargs)


    class Meta:
        verbose_name_plural = "06.专题课或学位课模块"


class CourseDetail(models.Model):
    """课程详情页内容"""
    course = models.OneToOneField("Course")
    hours = models.IntegerField("课时")
    course_slogan = models.CharField(max_length=125, blank=True, null=True)
    video_brief_link = models.CharField(verbose_name='课程介绍', max_length=255, blank=True, null=True)
    why_study = models.TextField(verbose_name="为什么学习这门课程")
    what_to_study_brief = models.TextField(verbose_name="我将学到哪些内容")
    career_improvement = models.TextField(verbose_name="此项目如何有助于我的职业生涯")
    prerequisite = models.TextField(verbose_name="课程先修要求", max_length=1024)
    recommend_courses = models.ManyToManyField("Course", related_name="recommend_by", blank=True)
    teachers = models.ManyToManyField("Teacher", verbose_name="课程讲师")

    def __str__(self):
        return "%s" % self.course

    class Meta:
        verbose_name_plural = "07.课程或学位模块详细"


class OftenAskedQuestion(models.Model):
    """常见问题"""
    content_type = models.ForeignKey(ContentType)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=1024)


    def __str__(self):
        return "%s-%s" % (self.content_object, self.question)


    class Meta:
        unique_together = ('content_type', 'object_id', 'question')
        verbose_name_plural = "08. 常见问题"


class CourseOutline(models.Model):
    """课程大纲"""
    course_detail = models.ForeignKey("CourseDetail")
    title = models.CharField(max_length=128)
    # 前端显示顺序
    order = models.PositiveSmallIntegerField(default=1)

    content = models.TextField("内容", max_length=2048)

    def __str__(self):
        return "%s" % self.title

    class Meta:
        unique_together = ('course_detail', 'title')
        verbose_name_plural = "09. 课程大纲"


class CourseChapter(models.Model):
    """课程章节"""
    course = models.ForeignKey("Course", related_name='coursechapters')
    chapter = models.SmallIntegerField(verbose_name="第几章", default=1)
    name = models.CharField(max_length=128)
    summary = models.TextField(verbose_name="章节介绍", blank=True, null=True)
    pub_date = models.DateField(verbose_name="发布日期", auto_now_add=True)

    class Meta:
        unique_together = ("course", 'chapter')
        verbose_name_plural = "10. 课程章节"

    def __str__(self):
        return "%s:(第%s章)%s" % (self.course, self.chapter, self.name)


class CourseSection(models.Model):
    """课时目录"""
    chapter = models.ForeignKey("CourseChapter", related_name='coursesections')
    name = models.CharField(max_length=128)
    order = models.PositiveSmallIntegerField(verbose_name="课时排序", help_text="建议每个课时之间空1至2个值，以备后续插入课时")
    section_type_choices = ((0, '文档'), (1, '练习'), (2, '视频'))
    section_type = models.SmallIntegerField(default=2, choices=section_type_choices)
    section_link = models.CharField(max_length=255, blank=True, null=True, help_text="若是video，填vid,若是文档，填link")
    video_time = models.CharField(verbose_name="视频时长", blank=True, null=True, max_length=32)  # 仅在前端展示使用
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)
    free_trail = models.BooleanField("是否可试看", default=False)

    class Meta:
        unique_together = ('chapter', 'section_link')
        verbose_name_plural = "11. 课时"

    def __str__(self):
        return "%s-%s" % (self.chapter, self.name)


class Homework(models.Model):
    chapter = models.ForeignKey("CourseChapter")
    title = models.CharField(max_length=128, verbose_name="作业题目")
    order = models.PositiveSmallIntegerField("作业顺序", help_text="同一课程的每个作业之前的order值间隔1-2个数")
    homework_type_choices = ((0, '作业'), (1, '模块通关考核'))
    homework_type = models.SmallIntegerField(choices=homework_type_choices, default=0)
    requirement = models.TextField(max_length=1024, verbose_name="作业需求")
    threshold = models.TextField(max_length=1024, verbose_name="踩分点")
    recommend_period = models.PositiveSmallIntegerField("推荐完成周期(天)", default=7)
    scholarship_value = models.PositiveSmallIntegerField("为该作业分配的奖学金(贝里)")
    note = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True, help_text="本作业如果后期不需要了，不想让学员看到，可以设置为False")

    class Meta:
        unique_together = ("chapter", "title")
        verbose_name_plural = "12. 章节作业"

    def __str__(self):
        return "%s - %s" % (self.chapter, self.title)


# class CourseReview(models.Model):
#     """课程评价"""
#     enrolled_course = models.OneToOneField("EnrolledCourse")
#     about_teacher = models.FloatField(default=0, verbose_name="讲师讲解是否清晰")
#     about_video = models.FloatField(default=0, verbose_name="内容实用")
#     about_course = models.FloatField(default=0, verbose_name="课程内容通俗易懂")
#     review = models.TextField(max_length=1024, verbose_name="评价")
#     disagree_number = models.IntegerField(default=0, verbose_name="踩")
#     agree_number = models.IntegerField(default=0, verbose_name="赞同数")
#     tags = models.ManyToManyField("Tags", blank=True, verbose_name="标签")
#     date = models.DateTimeField(auto_now_add=True, verbose_name="评价日期")
#     is_recommend = models.BooleanField("热评推荐", default=False)
#     hide = models.BooleanField("不在前端页面显示此条评价", default=False)
#
#     def __str__(self):
#         return "%s-%s" % (self.enrolled_course.course, self.review)
#
#     class Meta:
#         verbose_name_plural = "13. 课程评价（购买课程后才能评价）"
#
#
# class DegreeCourseReview(models.Model):
#     """学位课程评价
#     为了以后可以定制单独的评价内容，所以不与普通课程的评价混在一起，单独建表
#     """
#     enrolled_course = models.ForeignKey("EnrolledDegreeCourse")
#     course = models.ForeignKey("Course", verbose_name="评价学位模块", blank=True, null=True,
#                                help_text="不填写即代表评价整个学位课程", limit_choices_to={'course_type': 2})
#     about_teacher = models.FloatField(default=0, verbose_name="讲师讲解是否清晰")
#     about_video = models.FloatField(default=0, verbose_name="视频质量")
#     about_course = models.FloatField(default=0, verbose_name="课程")
#     review = models.TextField(max_length=1024, verbose_name="评价")
#     disagree_number = models.IntegerField(default=0, verbose_name="踩")
#     agree_number = models.IntegerField(default=0, verbose_name="赞同数")
#     tags = models.ManyToManyField("Tags", blank=True, verbose_name="标签")
#     date = models.DateTimeField(auto_now_add=True, verbose_name="评价日期")
#     is_recommend = models.BooleanField("热评推荐", default=False)
#     hide = models.BooleanField("不在前端页面显示此条评价", default=False)
#
#     def __str__(self):
#         return "%s-%s" % (self.enrolled_course, self.review)
#
#     class Meta:
#         verbose_name_plural = "14. 学位课评价（购买课程后才能评价）"


class PricePolicy(models.Model):
    """价格与有课程效期表"""
    content_type = models.ForeignKey(ContentType)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # course = models.ForeignKey("Course")
    valid_period_choices = ((1, '1天'), (3, '3天'),
                            (7, '1周'), (14, '2周'),
                            (30, '1个月'),
                            (60, '2个月'),
                            (90, '3个月'),
                            (180, '6个月'), (210, '12个月'),
                            (540, '18个月'), (720, '24个月'),
                            )
    valid_period = models.SmallIntegerField(choices=valid_period_choices)
    price = models.FloatField()

    class Meta:
        unique_together = ("content_type", 'object_id', "valid_period")
        verbose_name_plural = "15. 价格策略"

    def __str__(self):
        return "%s(%s)%s" % (self.content_object, self.get_valid_period_display(), self.price)

