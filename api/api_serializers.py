from api import models
from rest_framework import serializers


# 序列化评论的类
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course  # Course表
        fields = "__all__"  # 序列化所有字段
        # 定义额外的参数
        extra_kwargs = {
            "content": {
                "error_messages": {
                    "required": '内容不能为空',
                }
            },
            "article": {
                "error_messages": {
                    "required": '文章不能为空'
                }
            }
        }
