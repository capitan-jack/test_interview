from django.db import models
from django.contrib.auth.models import User


class AppointmentSlot(models.Model):
	'''database table to store sales reps appointment slots'''
	class Meta:
		db_table = "appointment_slots"

	user = models.ForeignKey(User,
							 related_name='slots')
	date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	soft_deleted = models.BooleanField(default=False)


class DemoAppointment(models.Model):
	'''db table to store demo requests by clients,
	   only considering email id as representation of client 
	   for now'''
	class Meta:
		db_table = "appointments"

	user = models.ForeignKey(User,
							 related_name='appointments',
							 null=True, default=None)
	date = models.DateField()
	start_time = models.TimeField()
	client_email = models.EmailField(
        verbose_name='email address',
        max_length=255,
    )
	scheduled = models.BooleanField(default=False)
	soft_deleted = models.BooleanField(default=False)


class UserCalender(models.Model):
	calender_id = models.CharField(max_length=255)
	user = models.ForeignKey(User, related_name='caleder')
	refresh_token = models.CharField(max_length=255)