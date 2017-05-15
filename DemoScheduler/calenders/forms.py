from django import forms
from django.utils.dateparse import parse_date
import datetime
import time
from .models import AppointmentSlot, DemoAppointment, UserCalender
from .services import get_available_slots_by_date, get_next_sales_rep,\
    schedule_g_calendar_event


class NotValidatedMultipleChoiceFiled(forms.TypedMultipleChoiceField):
    """Field that do not validate if the field values are in self.choices"""

    def to_python(self, value):
        """Override checking method"""
        return map(self.coerce, value)

    def validate(self, value):
        """Nothing to do here"""
        pass


class AppointmentSlotsForm(forms.Form):
    date = NotValidatedMultipleChoiceFiled()
    start_time = forms.TimeField()
    end_time = forms.TimeField()

    def clean_date(self):
        dates = []
        print(self.cleaned_data['date'])
        for date_str in self.cleaned_data['date']:
            dates.append(datetime.datetime.\
                strptime(date_str, '%Y-%m-%d').date())
        print(dates)
        return dates

    def save(self, user):
        for date in self.cleaned_data['date']:
            print("here")
            slot = AppointmentSlot()
            slot.date = date
            slot.start_time = self.cleaned_data['start_time']
            slot.end_time = self.cleaned_data['end_time']
            slot.user = user
            slot.save()


class DemoScheduleForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        date = datetime.date(kwargs.pop('year'),
                             kwargs.pop('month'),
                             kwargs.pop('day'))
        super(DemoScheduleForm, self).__init__(*args, **kwargs)
        self._date = date
        avail_slots = get_available_slots_by_date(date)
        self.fields['demo_slot'] = \
            forms.\
            ChoiceField(choices=list(map(lambda time: (time,str(time)), avail_slots)))


    def save(self):
        appointment = DemoAppointment()
        appointment.date = self._date
        appointment.start_time = self.cleaned_data['demo_slot']
        appointment.client_email = self.cleaned_data['email']
        appointment.scheduled = False
        appointment.soft_deleted = False
        appointment.user = get_next_sales_rep(appointment.date, 
                                              appointment.start_time)
        appointment.save()
        schedule_g_calendar_event(appointment)


class CalendarAttachForm(forms.Form):
    calender_id = forms.CharField()
    refresh_token = forms.CharField()

    def save(self, user):
        calender = UserCalender()
        calender.user = user
        calender.calender_id = self.cleaned_data['calender_id']
        calender.refresh_token = self.cleaned_data['refresh_token']
        calender.save()

