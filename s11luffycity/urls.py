"""s11luffycity URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from api import api_urls
from api.views import html

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/(?P<version>\w+)/', include(api_urls)),
    url(r'^$', html.index),
    url(r'^index/$', html.index),
    url(r'^login/$', html.login),
    url(r'^logout/$', html.logout),
    url(r'^course/$', html.course),
    url(r'course/(?P<pk>\d+)/$',html.course_detail),
    url(r'^news/$', html.news),
    url(r'^shopping_cart/$', html.shopping_cart),
]


