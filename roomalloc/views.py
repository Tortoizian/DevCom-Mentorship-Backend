from django.shortcuts import render
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from datetime import datetime


# Auth views

@method_decorator(csrf_protect, name='dispatch')
class CheckAuthenticatedView(APIView):
	permission_classes = (permissions.AllowAny, )

	def get(self, request : HttpRequest, format=None):
		try:
			isAuthenticated = request.user.is_authenticated
			if isAuthenticated:
				return Response({'isAuthenticated':'true'})
			else:
				return Response({'isAuthenticated':'false'})
		except:
			return Response({'error': "Could not check authentication status"})

@method_decorator(csrf_protect, name='dispatch')
class SignupView(APIView):
	permission_classes = (permissions.AllowAny, )

	def post(self, request : HttpRequest, format=None):
		data = self.request.data

		rollno = data["rollno"]
		student_name = data["student_name"]
		student_dept = data["student_dept"]
		email = data["email"]
		password = data["password"]
		re_password = data["re_password"]

		if password == re_password:
			try:
				if Student.objects.filter(username=rollno).exists():
					return Response({'error': "rollno already exists"})
				elif Student.objects.filter(email=email).exists():
					return Response({'error': "email already exists"})
				else:
					user = Student.objects.create_user(username=rollno, student_name=student_name, student_dept=student_dept, email=email, password=password)
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
			rollno = data["rollno"]
			password = data["password"]

			user = authenticate(username=rollno, password=password)

			if user is not None:
				login(request, user)
				return Response({'success': "User authenticated", 'rollno': rollno})
			else:
				return Response({'error':"Error while authenticating"})
		except:
			return Response({'error': "Could not log user in",'request':request.data})
			

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
			user = request.user

			user = Student.objects.filter(username=user.username).delete()
			return Response({'success': "User deleted successfully"})
		except:
			return Response({'error': "Could not delete user"})
		
class GetUsersView(APIView):
	permission_classes  = (permissions.AllowAny, )

	def get(self, request : HttpRequest, format=None):
		users = Student.objects.all()

		users = StudentSerializer(users, many=True)
		return Response(users.data)

# Other views

class StudentView(APIView): # just for testing purposes
	serializer_class = StudentSerializer

	def get(self, request : HttpRequest):
		students = Student.objects.all()
		serializer = StudentSerializer(students, many=True)
		return Response(serializer.data)
	
	def post(self, request : HttpRequest):
		serializer = StudentSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)

class StudentBookings(APIView): #for viewing a specific student's bookings and making a new booking.
	serializer_class = BookingSerializer

	def get(self,request : HttpRequest, *args, **kwargs):
		student = request.user
		bookings = Booking.objects.filter(booking_by=student)
		serializer=BookingSerializer(bookings, many=True)
		return Response(serializer.data)

	def post(self, request : HttpRequest, *args, **kwargs):
		serializer = BookingSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			data = serializer.validated_data
			room = data.get('booking_room')
			slot = data.get('slot')
			user = request.user
			date = data.get('date')

			#Check 1-Two rooms cannot be booked in overlapping slots
			#prevent double booking: same room cannot be booked for any overlapping slot duration
			if Booking.objects.filter(
				booking_room=room
			).filter(
				Q(slot__start_time__lt=slot.end_time) & Q(slot__end_time__gt=slot.start_time) & Q(date=date)

			).exists():
				return Response({'error': 'Room is already booked under an interfering slot.'}, status=400)
			
			#Check 2- One user cannot have more than booking in overlapping slots

			if Booking.objects.filter(
				booking_by=user
			).filter(
				Q(slot__start_time__lt=slot.end_time) & Q(slot__end_time__gt=slot.start_time) &Q(date=date)
			).exists():
				return Response({'error' : 'One user cannot make 2 booking in an overlapping duration.'}, status=400)
			serializer.save(booking_by=user)
			return Response(serializer.data)

class SlotView(APIView): #optional for now
	serializer_class = SlotSerializer

	def get(self,request : HttpRequest):
		slots=Slot.objects.all()
		serializer = SlotSerializer(slots, many=True)
		return Response(serializer.data)

	def post(self, request : HttpRequest):
		serializer = SlotSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)

class RoomView(APIView): #Either for viewing all rooms or only available rooms
	serializer_class = RoomSerializer

	def get(self,request : HttpRequest): #Using query parameters for slot and date, GET /room/?slot=uuid&date=2025-01-25
			try:
				slot_id = request.query_params.get('slot')
				date_str = request.query_params.get('date')
				if slot_id and date_str:
					date = datetime.fromisoformat(date_str).date()
					slot = get_object_or_404(Slot, slot_id=slot_id)
					booked_rooms = Booking.objects.filter(slot=slot, date=date).values_list('booking_room_id', flat=True)
					avail_rooms = Room.objects.exclude(room_id__in=booked_rooms)
					serializer = RoomSerializer(avail_rooms, many=True)
					return Response({'available_rooms': serializer.data})
				else:
					Rooms = Room.objects.all()
					serializer = RoomSerializer(Rooms, many=True)
					return Response({'available_rooms': serializer.data})
			except:
				return Response({'error' : 'Could not fetch rooms'}, status=400)

	def post(self, request : HttpRequest):
		serializer = RoomSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)