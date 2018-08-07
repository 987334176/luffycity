from django.conf.urls import url
from api.views import course

urlpatterns = [
    # url(r'login/$', views.LoginView.as_view()),
    url(r'courses/',course.CoursesView.as_view())
]