from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
	class Meta:
		model = Room
		fields = ['room_id', 'room_name', 'room_capacity']

		def validate_room_capacity(self, value):
			if value < 0:
				raise serializers.ValidationError("Room capacity must be positive.")
			return value

class StudentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Student
		fields = ['rollno', 'student_name', 'student_dept', 'email']

class SlotSerializer(serializers.ModelSerializer):
	class Meta:
		model = Slot
		fields = ['slot_id', 'start_time', 'end_time', 'day']

	def validate(self, data):
		start_time =  data.get('start_time')
		end_time =  data.get('end_time')
		day = data.get('day')

		# ensure start time is less than end time
		if start_time and end_time and end_time <= start_time:
			raise serializers.ValidationError("End time must be greater than start time")
	
		# ensure that the given day is in the acceptable format
		valid_days = [choice[0] for choice in Slot.DAY_CHOICES]
		if day not in valid_days:
			raise serializers.ValidationError(f"Day must be one of the following: {', '.join(valid_days)}.")

		return data

class BookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['booking_id', 'booking_room', 'booking_by', 'slot', 'date']

	def validate(self, data):
		room = data.get('booking_room')
		slot = data.get('slot')

		# ensure room isn't already booked for the given slot
		if Booking.objects.filter(booking_room=room, slot=slot).exists():
			raise serializers.ValidationError("The selected room is already booked for this slot.")

		# ensure the room exists
		if not Room.objects.filter(room_id=room.room_id).exists():
			raise serializers.ValidationError("The selected room does not exist.")

		# ensure the slot exists
		if not Slot.objects.filter(slot_id=slot.slot_id).exists():
			raise serializers.ValidationError("The selected slot does not exist.")
		
		return data