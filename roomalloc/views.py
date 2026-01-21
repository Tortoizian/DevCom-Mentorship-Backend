from django.shortcuts import render
from django.http import HttpRequest
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

# Auth views

@method_decorator(csrf_protect, name='dispatch')
class CheckAuthenticatedView(APIView):
	def get(self, request : HttpRequest, format=None):
		try:
			isAuthenticated = User.is_authenticated
			if isAuthenticated:
				return Response({'isAuthenticated':'success'})
			else:
				return Response({'isAuthenticated':'error'})
		except:
			return Response({'error': "Could not check authentication status"})

@method_decorator(csrf_protect, name='dispatch')
class SignupView(APIView):
	permission_classes = (permissions.AllowAny, )

	def post(self, request : HttpRequest, format=None):
		data = self.request.data

		username = data["username"]
		password = data["password"]
		re_password = data["re_password"]

		if password == re_password:
			try:
				if User.objects.filter(username=username).exists():
					return Response({'error': "Username already exists"})
				else:
					user = User.objects.create_user(username=username, password=password)
					user.save()
					return Response({'success': 'User created successfully!'})
			except:
				return Response({'error': "Could not register user"})
		else:
			return Response({'error': "Passwords do not match"})

@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(APIView):
	permission_classes = (permissions.AllowAny, )

	def get(self, request : HttpRequest, format=None):
		return Response({'success' : "CSRF cookie set"})
	
@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(APIView):
	permission_classes = (permissions.AllowAny, )

	def post(self, request : HttpRequest, format=None):
		try:
			data = self.request.data
			username = data["username"]
			password = data["password"]

			user = authenticate(username=username, password=password)

			if user is not None:
				login(request, user)
				return Response({'success': "User authenticated", 'username': username})
			else:
				return Response({'error':"Error while authenticating"})
		except:
			return Response({'error': "Could not log user in"})

class LogoutView(APIView):
	def post(self, request : HttpRequest, format=None):
		try:
			logout(request)
			return Response({'success':"User logged out"})
		except:
			return Response({'error': "Something went wrong while logging out"})
		
class DeleteUserView(APIView):
	def delete(self, request : HttpRequest, format=None):
		try:
			user = User.objects.user

			user = User.objects.filter(id=user.id).delete()
			return Response({'success': "User deleted successfully"})
		except:
			return Response({'error': "Could not delete user"})
		
class GetUsersView(APIView):
	permission_classes  = (permissions.AllowAny, )

	def get(self, request : HttpRequest, format=None):
		users = User.objects.all()

		users = UserSerializer(users, many=True)
		return Response(users.data)

# Other views

class StudentView(APIView):
	serializer_class = StudentSerializer

	def get(self, request : HttpRequest):
		output = [{'rollno': output.rollno, 'student_name': output.student_name, 'student_dept': output.student_dept, 'email': output.email} for output in Student.objects.all()]
		return Response(output)
	
	def post(self, request : HttpRequest):
		serializer = StudentSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)