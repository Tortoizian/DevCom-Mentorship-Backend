from django.db import models

# Create your models here.
class Room(models.Model):
	room_id = models.IntegerField(primary_key=True, unique=True)
	room_name = models.CharField(max_length=64)
	room_capacity = models.IntegerField()

	def __str__(self):
		return (f"roomid: {self.room_id}, Name: {self.room_name}, Capacity: {self.room_capacity}")

class Student(models.Model):
	rollno = models.CharField(max_length=10, primary_key=True)
	student_name = models.CharField(max_length=100)
	student_dept = models.CharField(max_length=64)

	def __str__(self):
		return (f"Roll No.: {self.rollno}, Name: {self.student_name}, Department: {self.student_dept}")


class Slot(models.Model):
	slot_id = models.AutoField(primary_key=True, unique=True)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	#is_available needed?

	def __str__(self):
		return (f"Start Time:{self.start_time.strftime('%H:%M')}, End Time:{self.end_time.strftime('%H:%M')}")
	


class Booking(models.Model):
	booking_id = models.AutoField(primary_key=True, unique=True)
	booking_room = models.ForeignKey(Room, on_delete=models.RESTRICT) # references the room_id key
	booking_by = models.ForeignKey(Student, on_delete=models.RESTRICT) # references the rollno key
	slot = models.ForeignKey(Slot, on_delete=models.RESTRICT)

	def __str__(self):
		return (f"Booking ID: {self.booking_id}, Room: {self.booking_room}, Student: {self.booking_by}, Slot:{self.slot}")
	


