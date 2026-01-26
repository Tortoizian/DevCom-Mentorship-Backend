from django.shortcuts import render
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from datetime import datetime


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

class StudentView(APIView): # just for testing purposes
	serializer_class = StudentSerializer

	def get(self, request : HttpRequest):
		output = [{'rollno': output.rollno, 'student_name': output.student_name, 'student_dept': output.student_dept, 'email': output.email} for output in Student.objects.all()]
		return Response(output)
	
	def post(self, request : HttpRequest):
		serializer = StudentSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)

class StudentBookings(APIView): #for viewing a specific student's bookings and making a new booking.
	serializer_class = BookingSerializer

	def get(self,request : HttpRequest, *args, **kwargs): 
		rollno = kwargs.get('rollno')
		if(rollno):
			bookings = Booking.objects.filter(booking_by=rollno)
		else:
			bookings = Booking.objects.all()
		serializer=BookingSerializer(bookings, many=True)
		
		
		return Response(serializer.data)

	def post(self, request : HttpRequest, *args, **kwargs):
		serializer = BookingSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			data = serializer.validated_data
			room = data.get('booking_room')
			slot = data.get('slot')
			user = data.get('booking_by')
			#Check 1-Two rooms cannot be booked in overlapping slots
			#prevent double booking: same room cannot be booked for any overlapping slot duration
			if Booking.objects.filter(
				booking_room=room
			).filter(
				Q(slot__start_time__lt=slot.end_time) & Q(slot__end_time__gt=slot.start_time)
			).exists():
				return Response({'error': 'Room is already booked under an interfering slot.'}, status=400)
			
			#Check 2- One user cannot have more than booking in overlapping slots

			if Booking.objects.filter(
				booking_by=user
			).filter(
				Q(slot__start_time__lt=slot.end_time) & Q(slot__end_time__gt=slot.start_time)
			).exists():
				return Response({'error' : 'One user cannot make 2 booking in an overlapping duration.'}, status=400)
			serializer.save()
			return Response(serializer.data)

class SlotView(APIView): #optional for now
	serializer_class = SlotSerializer

	def get(self,request : HttpRequest):
		output = [{'slot_id': output.slot_id, 'start_time': output.start_time, 'end_time': output.end_time, 'day': output.day} for output in Slot.objects.all()]
		return Response(output)

	def post(self, request : HttpRequest):
		serializer = SlotSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)

class AvailRoomView(APIView): #This view is for viewing only available room views(in a slot)
	serializer_class = RoomSerializer

	def get(self,request : HttpRequest): #Using query paramteres for datetime, GET /bookings/?start-dt=2025-01-25T14:30:00&end-dt=2025-01-25T15:00:00
			try:
				start_dt = datetime.fromisoformat(request.query_params.get('start-dt'))
				end_dt=datetime.fromisoformat(request.query_params.get('end-dt'))
				overlapped_bookings=Booking.objects.filter(Q(slot__start_time__lt=end_dt) & Q(slot__end_time__gt=start_dt)) #getting bookings that overlap with start_dt to end_dt
				booked_room_ids = overlapped_bookings.values_list('booking_room_id', flat=True)
				avail_rooms=Room.objects.exclude(room_id__in=booked_room_ids)
				serializer = RoomSerializer(avail_rooms, many=True)
				return Response({'available_rooms': serializer.data})
			except:
				return Response({'error' : 'Use datetime in ISO format'}, status=400)

	

class RoomView(APIView): #This view is for displaying ALL rooms. Also for adding a new room to the db.

	def get(self,request : HttpRequest):
		Rooms = Room.objects.all()
		serializer = RoomSerializer(Rooms, many=True)
		return Response(serializer.data)
	
	def post(self, request : HttpRequest):
		serializer = RoomSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data)
		
