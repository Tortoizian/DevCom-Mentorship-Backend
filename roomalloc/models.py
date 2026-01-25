import uuid
from django.db import models
from django.utils import timezone

# Create your models here.
class Room(models.Model):
	room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	room_name = models.CharField(max_length=64)
	room_capacity = models.IntegerField()
	is_booked = models.BooleanField()

	def __str__(self):
		return (f"Room: {self.room_name}, Capacity: {self.room_capacity}")

class Student(models.Model):
	rollno = models.CharField(max_length=10, primary_key=True, unique=True)
	student_name = models.CharField(max_length=100)
	student_dept = models.CharField(max_length=64)
	email = models.EmailField(max_length=254, unique=True, null=True, blank=True)

	def __str__(self):
		return (f"Roll No: {self.rollno}, Name: {self.student_name}, Dept: {self.student_dept}, Email: {self.email}")


class Slot(models.Model):
	slot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
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
		return (f"Date: {timezone.localtime(self.start_time).strftime('%d-%m-%Y')}, Start Time: {timezone.localtime(self.start_time).strftime('%H:%M')}, End Time: {timezone.localtime(self.end_time).strftime('%H:%M')}")
	


class Booking(models.Model):
	booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	booking_room = models.ForeignKey(Room, on_delete=models.RESTRICT) # references the room_id key
	booking_by = models.ForeignKey(Student, on_delete=models.RESTRICT) # references the rollno key
	slot = models.ForeignKey(Slot, on_delete=models.RESTRICT)

	def __str__(self):
		return (f"Room: {self.booking_room.room_name}; Student: {self.booking_by.rollno}; Slot: ({self.slot})")