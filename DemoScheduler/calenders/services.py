from .models import AppointmentSlot, DemoAppointment
from django.contrib.auth.models import User
from django.db.models import Q
import datetime
from django.conf import settings
from oauth2client.contrib import xsrfutil
import httplib2
from apiclient import discovery
from oauth2client import client, GOOGLE_TOKEN_URI, GOOGLE_REVOKE_URI
from oauth2client.file import Storage
from oauth2client import tools
from oauth2client.client import GoogleCredentials
import httplib2
import os


'''compute available slots for a date. basically counts all
    available slots to 30 minute gaps. removes slots which 
    already have appointments. return slot availability list'''
def get_available_slots_by_date(date):
    available_slots = dict()
    app_slots = AppointmentSlot.objects.filter(date=date).all()
    for slot in app_slots:
        start = slot.start_time
        while start<slot.end_time:
            available_slots[str(start)] = available_slots.get(str(start), 0)+1
            temp = datetime.datetime.combine(date, start) + \
            datetime.timedelta(minutes=30)
            start = temp.time()
    appointments = DemoAppointment.objects.filter(date=date).all()
    for appointment in appointments:
        available_slots[str(appointment.start_time)] = \
        available_slots[str(appointment.start_time)] - 1
    available_slots_list = []
    for key, value in available_slots.items():
        if value>0:
            available_slots_list.\
            append(datetime.time(*list(map(int,key.split(':')))))
    return available_slots_list


'''compute sales reps available for given date and time.
    return sales rep with min appointments scheduled for date'''
def get_next_sales_rep(date, time):
    available_users = User.objects.\
        filter(Q(slots__date=date) & \
               Q(slots__start_time__lte=time) & \
               Q(slots__end_time__gt=time)).\
        filter(~Q(appointments__start_time=time)).all()
    return min([u for u in available_users],
               key=lambda user: len(user.appointments.filter(date=date).all()))


def schedule_g_calendar_event(appointment):
    credentials = client.OAuth2Credentials(
    None, settings.G_CLIENT_ID, settings.G_CLIENT_SECRET, 
    appointment.user.caleder.first().refresh_token, None, GOOGLE_TOKEN_URI,
    None, revoke_uri=GOOGLE_REVOKE_URI)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = {
        'summary': 'Scribe Demo',
        'location': 'Online',
        'description': 'Scribe demo',
        'start': {
            'dateTime': str(datetime.datetime.combine(appointment.date, appointment.start_time)),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': str(datetime.datetime.combine(appointment.date, appointment.start_time)) +\
                datetime.timedelta(minutes=30),
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': appointment.client_email},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    event = service.events().insert(calendarId=appointment.user.caleder.first().calender_id, body=event).execute()
