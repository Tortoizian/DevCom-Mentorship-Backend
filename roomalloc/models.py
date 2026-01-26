import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class Room(models.Model):
	room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	room_name = models.CharField(max_length=64)
	room_capacity = models.IntegerField()

	def __str__(self):
		return (f"Room: {self.room_name}, Capacity: {self.room_capacity}")

class Student(AbstractUser):
	username = models.CharField("Roll No.", max_length=10, unique=True, primary_key=True) # the roll will be used as username
	student_name = models.CharField(max_length=100)
	student_dept = models.CharField(max_length=64)
	email = models.EmailField(max_length=254, unique=True)

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['student_name', 'student_dept', 'email']

	def __str__(self):
		# return (f"Roll No: {self.username}, Name: {self.student_name}, Dept: {self.student_dept}, Email: {self.email}")
		return (f"{self.student_name} ({self.username})")


class Slot(models.Model):
	slot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	start_time = models.TimeField()
	end_time = models.TimeField()
	DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
	day = models.CharField(max_length=64,choices=DAY_CHOICES)

	def __str__(self):
		return (f"{self.start_time} to {self.end_time} on {self.day}")
	


class Booking(models.Model):
	booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	booking_room = models.ForeignKey(Room, on_delete=models.RESTRICT) # references the room_id key
	booking_by = models.ForeignKey(Student, on_delete=models.RESTRICT) # references the username key
	slot = models.ForeignKey(Slot, on_delete=models.RESTRICT)
	date = models.DateField()

	def __str__(self):
		return (f"Room: {self.booking_room.room_name}; Student: {self.booking_by.rollno}; Slot: ({self.slot}); Date:{self.date}")