from django.conf.urls import url
from django_calendar import views

app_name = 'django_calendar'

urlpatterns = [
    url(r'^$', views.CalendarView.as_view(), name='calendar'),
    url(r'^(?P<year>[0-9]+)/(?P<month>[0-9]+)/$',
        views.CalendarView.as_view(), name='calendar'),
    url(
        (
            r'^schedule_create/'
            r'(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$'
        ),
        views.ScheduleCreateView.as_view(),
        name='schedule_create'),
    url(
        (
            r'^schedule_list/'
            r'(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$'
        ),
        views.ScheduleListView.as_view(),
        name='schedule_list'),
]
