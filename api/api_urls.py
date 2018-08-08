from django.conf.urls import url
from api.views import course,degreecourse,auth,shoppingcart

urlpatterns = [
    url(r'auth/$', auth.AuthView.as_view({'post':'login'})),
    url(r'courses/$',course.CoursesView.as_view()),
    url(r'courses/(?P<pk>\d+)/$',course.CourseDetailView.as_view()),
    url(r'courses/thematic/$',course.CourseThematicView.as_view()),
    url(r'courses/module/(?P<pk>\d+)/$',course.CourseModuleView.as_view()),
    url(r'courses/faq/(?P<pk>\d+)/$',course.CourseFAQView.as_view()),
    url(r'courses/outline/(?P<pk>\d+)/$',course.CourseOutlineView.as_view()),
    url(r'courses/chapter/(?P<pk>\d+)/$',course.CourseChapterView.as_view()),

    url(r'degreecourse/$',degreecourse.DegreeCourseView.as_view()),
    url(r'degreecourse/teachers/$',degreecourse.DegreeCourseTeachersView.as_view()),
    url(r'degreecourse/scholarship/$',degreecourse.DegreeCourseScholarshipView.as_view()),

    url(r'shoppingcart/$', shoppingcart.ShoppingCartView.as_view({'post':'create'})),
]