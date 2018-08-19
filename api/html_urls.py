from django.conf.urls import url
from api.views import html

urlpatterns = [
    url(r'', html.index),
    url(r'course/$', html.course),
]