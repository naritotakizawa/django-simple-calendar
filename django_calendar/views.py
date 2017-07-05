import datetime
from django.utils.safestring import mark_safe
from django.views import generic
from django.shortcuts import render

from .calendarlib import Calendar
from .forms import ScheduleForm
from .models import Schedule


class CalendarView(generic.TemplateView):
    """カレンダーを表示するビュー."""

    template_name = 'django_calendar/calendar.html'

    def get_context_data(self, *args, **kwargs):
        """カレンダーオブジェクトをcontextに追加する."""
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        # /アクセスの場合
        if year is None and month is None:
            date = datetime.datetime.now()

        # yearとmonthの指定がある場合
        elif year and month:
            date = datetime.datetime(
                year=int(year), month=int(month), day=1
            )

        month_html_calendar = Calendar(date).formatmonth()
        context = super().get_context_data(*args, **kwargs)

        # mark_safeでhtmlがエスケープされないようにする
        context['calendar'] = mark_safe(month_html_calendar)
        return context


class ScheduleCreateView(generic.CreateView):
    """スケジュールの作成ビュー."""

    model = Schedule
    form_class = ScheduleForm

    def form_valid(self, form):
        """スケジュールの日付に、該当の日付を入れて保存する."""
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        date = datetime.datetime(
            year=int(year), month=int(month), day=int(day))
        schedule = form.save(commit=False)
        schedule.date = date
        schedule.save()
        return render(self.request, 'django_calendar/close.html')


class ScheduleListView(generic.ListView):
    model = Schedule

    def get_queryset(self):
        """その日付のスケジュールを返す."""
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        date = datetime.datetime(
            year=int(year), month=int(month), day=int(day)
        )
        queryset = Schedule.objects.filter(
            date=date
        )
        return queryset
