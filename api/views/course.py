from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from rest_framework.versioning import URLPathVersioning

class CoursesView(APIView):
    def get(self,request,*args,**kwargs):
        result = ""
        if request.version == "v1":
            result = 'v1'
        else:
            result = "other"

        return HttpResponse(result)
