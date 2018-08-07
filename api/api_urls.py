from django.conf.urls import url
from api import views

urlpatterns = [
    # url(r'login/$', views.LoginView.as_view()),
]

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# 注册路由,表示路径comment对应视图函数CourseViewSet
router.register(r'course', views.CourseViewSet)
urlpatterns += router.urls
