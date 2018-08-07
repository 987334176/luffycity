from django.contrib import admin

# Register your models here.
from api import models
admin.site.register(models.CourseCategory)
admin.site.register(models.CourseSubCategory)
admin.site.register(models.DegreeCourse)
admin.site.register(models.Teacher)
admin.site.register(models.Scholarship)
admin.site.register(models.Course)
admin.site.register(models.CourseDetail)
admin.site.register(models.OftenAskedQuestion)
admin.site.register(models.CourseOutline)
admin.site.register(models.CourseChapter)
admin.site.register(models.CourseSection)
admin.site.register(models.Homework)
admin.site.register(models.PricePolicy)