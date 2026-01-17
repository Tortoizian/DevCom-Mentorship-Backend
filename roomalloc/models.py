from django.db import models

# Create your models here.
class Room(models.Model):
	roomID = models.IntegerField(primary_key=True, unique=True)
	roomName = models.CharField(max_length=64)
	roomCapacity = models.IntegerField()

	def __str__(self):
		return (f"roomid: {self.roomID}, Name: {self.roomName}, Capacity: {self.roomCapacity}")

class Student(models.Model):
	rollno = models.CharField(max_length=10, primary_key=True, unique=True)
	studentName = models.CharField(max_length=100)
	studentDept = models.CharField(max_length=64)

	def __str__(self):
		return (f"Roll No.: {self.rollno}, Name: {self.studentName}, Department: {self.studentDept}")

class Booking(models.Model):
	bookingID = models.AutoField(primary_key=True, unique=True)
	bookingRoom = models.ForeignKey(Room, on_delete=models.RESTRICT) # references the roomID key (can be changed). remember while implementing later
	bookingBy = models.ForeignKey(Student, on_delete=models.RESTRICT) # references the rollno key (can be changed). remember while implementing later
	slot=models.ForeignKey(Slot, on_delete=models.RESTRICT)

	def __str__(self):
		return (f"Booking ID: {self.bookingID}, Room: {self.BookingRoom}, Student: {self.BookingBy}")
	
class Slot(models.Model):
	slotID=models.AutoField(primary_key=True, unique=True)
	startTime=models.DateTimeField()
	endTime=models.DateTimeField()
	isAvailable=models.BooleanField(default=True)

	def __str__(self):
		return (f"Start Time:{self.startTime}, End Time:{self.endTime}, Availability:{self.isAvailable}")

