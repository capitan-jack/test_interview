from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from .forms import AppointmentSlotsForm, DemoScheduleForm, CalendarAttachForm
from oauth2client.contrib import xsrfutil
import httplib2
from oauth2client.client import OAuth2WebServerFlow
from googleapiclient.discovery import build
from django.conf import settings
import datetime


FLOW=OAuth2WebServerFlow(
		client_id=settings.G_CLIENT_ID,
		client_secret=settings.G_CLIENT_SECRET,
		scope=['https://www.googleapis.com/auth/calendar'],
		redirect_uri=settings.G_REDIRECT_URI
		)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('calenders:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def index(request):
	if request.method == 'POST':
	    form = AppointmentSlotsForm(request.POST)
	    if form.is_valid():
	        form.save(request.user)
	else:
		form = AppointmentSlotsForm()
	calendar_attached = False
	if request.user.caleder.first() != None:
		print(request.user.caleder)
		calendar_attached = True
	return render(request, 'calenders/landing.html',{'form':form, 'attach_calender':calendar_attached})


def available_slots(request, year=None, month=None, day=None):
	if year == None or month == None or day == None:
		return render(request, 'calenders/schedule_demo.html')
	if request.method == 'GET':
		form = DemoScheduleForm(year=int(year),month=int(month), day=int(day))
		return render(request, 'calenders/schedule_demo.html', {'form':form})
	if request.method == 'POST':
		form = DemoScheduleForm(request.POST, year=int(year),month=int(month), day=int(day))
		if form.is_valid():
			print("how")
			form.save()
			return render(request, 'calenders/schedule_demo.html', {'form':form})
	return render(request, 'calenders/schedule_demo.html')


def google_calender_permission(request):
	FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
												   request.user)
	FLOW.params['access_type'] = 'offline' 
	authorize_url = FLOW.step1_get_authorize_url()
	return HttpResponseRedirect(authorize_url)


def google_auth_return(request):
	if not xsrfutil.validate_token(settings.SECRET_KEY, request.GET.get('state').encode("utf-8"),request.user):
		return  HttpResponseBadRequest()
	credential = FLOW.step2_exchange(request.GET)
	print(credential.to_json())
	http = httplib2.Http()
	http = credential.authorize(http)
	service = build("calendar", "v3", http=http)
	calendar_data = service.calendarList().list().execute()
	for calendar in calendar_data['items']:
		if 'primary' in calendar and calendar['primary'] == True:
			form = CalendarAttachForm({'calender_id':calendar['id'], 'refresh_token':credential.refresh_token})
			if form.is_valid():
				form.save(request.user)
			return redirect('calenders:index')
	return redirect('calenders:index')
