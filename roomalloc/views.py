from django.shortcuts import render, redirect
from django.http import HttpRequest
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import RegistrationForm

# Auth Views
def register_view(request : HttpRequest):
	if request.method == "POST":
		form = RegistrationForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get("username")
			password = form.cleaned_data.get("password")
			user = User.objects.create_user(username=username, password=password)
			login(request, user) # Can be changed to decide whether to autologin on new user or not
			return redirect('home') # home page redirect, REM TO LINK
	else:
		form = RegistrationForm()
	return render(request, 'accounts/register.html', {'form': form}) # Register page, REM TO LINK

def login_view(request : HttpRequest):
	error_message = None
	if request.method == "POST":
		username = request.POST.get("username")
		password = request.POST.get("password")
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			next_url = request.POST.get('next') or request.GET.get('next') or 'home' # REM TO LINK
			return redirect(next_url)
		else:
			error_message = "Invalid Credentials..."
	return render(request, 'accounts/login.html', {'error': error_message}) # REM TO LINK

def logout_view(request : HttpRequest):
	if request.method == "POST":
		logout(request)
		return redirect('login') # REM TO LINK
	else:
		return redirect('home') # REM TO LINK

# Create your views here.
@login_required
def home_view(request : HttpRequest):
	return render(request, 'home.html') # REM TO LINK

class ProtectedView(LoginRequiredMixin, APIView):
	login_url = 'accounts/login/' # REM TO LINK
	# 'next' - to redirect url
	redirect_field_name = 'redirect_to'
	serializer_class = StudentSerializer

	def get(self, request : HttpRequest):
		output = [{'rollno': output.rollno, 'student_name': output.student_name, 'student_dept': output.student_dept, 'email': output.email} for output in Student.objects.all()]
		return Response(output)

	def post(self, request : HttpRequest):
		serializer = StudentSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)




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