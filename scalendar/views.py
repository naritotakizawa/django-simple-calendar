import calendar
from collections import deque
import datetime
from .models import Schedule


class BaseCalendarMixin:
    """カレンダー関連Mixinの、基底クラス"""
    first_weekday = 0  # 0は月曜から、1は火曜から。6なら日曜日からになります。お望みなら、継承したビューで指定してください。
    week_names = ['月', '火', '水', '木', '金', '土', '日']  # これは、月曜日から書くことを想定します。['Mon', 'Tue'...

    def setup(self):
        """カレンダーのセットアップ処理

        calendar.Calendarクラスの機能を利用するため、インスタンス化します。
        Calendarクラスのmonthdatescalendarメソッドを利用していますが、デフォルトが月曜日からで、
        火曜日から表示したい(first_weekday=1)、といったケースに対応するためのセットアップ処理です。

        """
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        """first_weekday(最初に表示される曜日)にあわせて、week_namesをシフトする"""
        week_names = deque(self.week_names)
        week_names.rotate(-self.first_weekday)
        return week_names


class MonthCalendarMixin(BaseCalendarMixin):
    """月間カレンダーの機能を提供するMixin"""

    @staticmethod
    def get_previous_month(date):
        """前月を返す"""
        if date.month == 1:
            return date.replace(year=date.year-1, month=12, day=1)

        else:
            return date.replace(month=date.month-1, day=1)

    @staticmethod
    def get_next_month(date):
        """次月を返す"""
        if date.month == 12:
            return date.replace(year=date.year+1, month=1, day=1)

        else:
            return date.replace(month=date.month+1, day=1)

    def get_month_days(self, date):
        """その月の全ての日を返す"""
        return self._calendar.monthdatescalendar(date.year, date.month)

    def get_current_month(self):
        """現在の月を返す"""
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if month and year:
            month = datetime.date(year=int(year), month=int(month), day=1)
        else:
            month = datetime.date.today().replace(day=1)
        return month

    def get_month_calendar(self):
        """月間カレンダー情報の入った辞書を返す"""
        self.setup()
        current_month = self.get_current_month()
        calendar_data = {
            'now': datetime.date.today(),
            'days': self.get_month_days(current_month),
            'current': current_month,
            'previous': self.get_previous_month(current_month),
            'next': self.get_next_month(current_month),
            'week_names': self.get_week_names(),
        }
        return calendar_data


class WeekCalendarMixin(BaseCalendarMixin):
    """週間カレンダーの機能を提供するMixin"""

    def get_week_days(self):
        """その週の日を全て返す"""
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if month and year and day:
            date = datetime.date(year=int(year), month=int(month), day=int(day))
        else:
            date = datetime.date.today().replace(day=1)
        for week in self._calendar.monthdatescalendar(date.year, date.month):
            if date in week:
                return week

    def get_week_calendar(self):
        """週間カレンダー情報の入った辞書を返す"""
        self.setup()
        days = self.get_week_days()
        first = days[0]
        last = days[-1]
        calendar_data = {
            'now': datetime.date.today(),
            'days': days,
            'previous': first - datetime.timedelta(days=7),
            'next': first + datetime.timedelta(days=7),
            'week_names': self.get_week_names(),
            'first': first,
            'last': last,
        }
        return calendar_data


class WeekWithScheduleMixin(WeekCalendarMixin):
    """スケジュール付きの、週間カレンダーを提供するMixin"""
    model = Schedule
    date_field = 'date'
    order_field = 'start_time'

    def get_week_schedules(self, days):
        """それぞれの日のスケジュールを返す"""
        for day in days:
            lookup = {self.date_field: day}
            queryset = self.model.objects.filter(**lookup)
            if self.order_field:
                queryset = queryset.order_by(self.order_field)
            yield queryset

    def get_week_calendar(self):
        calendar_data = super().get_week_calendar()
        schedules = self.get_week_schedules(calendar_data['days'])
        calendar_data['schedule_list'] = schedules
        return calendar_data


class MonthWithScheduleMixin(MonthCalendarMixin):
    """スケジュール付きの、月間カレンダーを提供するMixin"""
    model = Schedule
    date_field = 'date'
    order_field = 'start_time'

    def get_month_schedules(self, days):
        """(日付, その日のスケジュール)なリストを返す"""
        day_with_schedules = []
        for week in days:
            week_list = []
            for day in week:
                lookup = {self.date_field: day}
                queryset = self.model.objects.filter(**lookup)
                if self.order_field:
                    queryset = queryset.order_by(self.order_field)
                week_list.append(
                    (day, queryset)
                )
            day_with_schedules.append(week_list)
        return day_with_schedules

    def get_month_calendar(self):
        calendar_data = super().get_month_calendar()
        day_with_schedules = self.get_month_schedules(calendar_data['days'])
        calendar_data['days'] = day_with_schedules
        return calendar_data
