from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

app_name = 'calenders'
urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^available-slots/$', views.available_slots, name='available_slots'),
    url(r'^available-slots/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$', views.available_slots, name='available_slots'),
    url(r'^google_calender/$', views.google_calender_permission, name='google_calender_permission'),
	url(r'^attach_calender/$', views.google_auth_return, name='google_auth_return'),
        
]