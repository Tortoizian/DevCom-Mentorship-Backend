from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response

# Create your views here.
class StudentView(APIView):
	serializer_class = StudentSerializer

	def get(self, request):
		output = [{'rollno': output.rollno, 'student_name': output.student_name, 'student_dept': output.student_dept, 'email': output.email} for output in Student.objects.all()]
		return Response(output)
	
	def post(self, request):
		serializer = StudentSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)