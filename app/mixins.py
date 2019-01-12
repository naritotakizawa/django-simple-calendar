import calendar
from collections import deque
import datetime
import itertools
from django import forms


class BaseCalendarMixin:
    """カレンダー関連Mixinの、基底クラス"""
    first_weekday = 0  # 0は月曜から、1は火曜から。6なら日曜日からになります。お望みなら、継承したビューで指定してください。
    week_names = ['月', '火', '水', '木', '金', '土', '日']  # これは、月曜日から書くことを想定します。['Mon', 'Tue'...

    def setup(self):
        """内部カレンダーの設定処理

        calendar.Calendarクラスの機能を利用するため、インスタンス化します。
        Calendarクラスのmonthdatescalendarメソッドを利用していますが、デフォルトが月曜日からで、
        火曜日から表示したい(first_weekday=1)、といったケースに対応するためのセットアップ処理です。

        """
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        """first_weekday(最初に表示される曜日)にあわせて、week_namesをシフトする"""
        week_names = deque(self.week_names)
        week_names.rotate(-self.first_weekday)  # リスト内の要素を右に1つずつ移動...なんてときは、dequeを使うと中々面白いです
        return week_names


class MonthCalendarMixin(BaseCalendarMixin):
    """月間カレンダーの機能を提供するMixin"""

    def get_previous_month(self, date):
        """前月を返す"""
        if date.month == 1:
            return date.replace(year=date.year-1, month=12, day=1)
        else:
            return date.replace(month=date.month-1, day=1)

    def get_next_month(self, date):
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
            'month_days': self.get_month_days(current_month),
            'month_current': current_month,
            'month_previous': self.get_previous_month(current_month),
            'month_next': self.get_next_month(current_month),
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
            date = datetime.date.today()

        for week in self._calendar.monthdatescalendar(date.year, date.month):
            if date in week:  # 週ごとに取り出され、中身は全てdatetime.date型。該当の日が含まれていれば、それが今回表示すべき週です
                return week

    def get_week_calendar(self):
        """週間カレンダー情報の入った辞書を返す"""
        self.setup()
        days = self.get_week_days()
        first = days[0]
        last = days[-1]
        calendar_data = {
            'now': datetime.date.today(),
            'week_days': days,
            'week_previous': first - datetime.timedelta(days=7),
            'week_next': first + datetime.timedelta(days=7),
            'week_names': self.get_week_names(),
            'week_first': first,
            'week_last': last,
        }
        return calendar_data


class WeekWithScheduleMixin(WeekCalendarMixin):
    """スケジュール付きの、週間カレンダーを提供するMixin"""

    def get_week_schedules(self, start, end, days):
        """それぞれの日とスケジュールを返す"""
        lookup = {
            # '例えば、date__range: (1日, 31日)'を動的に作る
            '{}__range'.format(self.date_field): (start, end)
        }
        # 例えば、Schedule.objects.filter(date__range=(1日, 31日)) になる
        queryset = self.model.objects.filter(**lookup)

        # {1日のdatetime: 1日のスケジュール全て, 2日のdatetime: 2日の全て...}のような辞書を作る
        day_schedules = {day: [] for day in days}
        for schedule in queryset:
            schedule_date = getattr(schedule, self.date_field)
            day_schedules[schedule_date].append(schedule)
        return day_schedules

    def get_week_calendar(self):
        calendar_context = super().get_week_calendar()
        calendar_context['week_day_schedules'] = self.get_week_schedules(
            calendar_context['week_first'],
            calendar_context['week_last'],
            calendar_context['week_days']
        )
        return calendar_context


class MonthWithScheduleMixin(MonthCalendarMixin):
    """スケジュール付きの、月間カレンダーを提供するMixin"""

    def get_month_schedules(self, start, end, days):
        """それぞれの日とスケジュールを返す"""
        lookup = {
            # '例えば、date__range: (1日, 31日)'を動的に作る
            '{}__range'.format(self.date_field): (start, end)
        }
        # 例えば、Schedule.objects.filter(date__range=(1日, 31日)) になる
        queryset = self.model.objects.filter(**lookup)

        # {1日のdatetime: 1日のスケジュール全て, 2日のdatetime: 2日の全て...}のような辞書を作る
        day_schedules = {day: [] for week in days for day in week}
        for schedule in queryset:
            schedule_date = getattr(schedule, self.date_field)
            day_schedules[schedule_date].append(schedule)

        # day_schedules辞書を、周毎に分割する。[{1日: 1日のスケジュール...}, {8日: 8日のスケジュール...}, ...]
        # 7個ずつ取り出して分割しています。
        size = len(day_schedules)
        return [{key: day_schedules[key] for key in itertools.islice(day_schedules, i, i+7)} for i in range(0, size, 7)]

    def get_month_calendar(self):
        calendar_context = super().get_month_calendar()
        month_days = calendar_context['month_days']
        month_first = month_days[0][0]
        month_last = month_days[-1][-1]
        calendar_context['month_day_schedules'] = self.get_month_schedules(
            month_first,
            month_last,
            month_days
        )
        return calendar_context


class MonthWithFormsMixin(MonthCalendarMixin):
    """スケジュール付きの、月間カレンダーを提供するMixin"""

    def get_month_forms(self, start, end, days):
        """それぞれの日と紐づくフォームを作成する"""
        lookup = {
            # '例えば、date__range: (1日, 31日)'を動的に作る
            '{}__range'.format(self.date_field): (start, end)
        }
        # 例えば、Schedule.objects.filter(date__range=(1日, 31日)) になる
        queryset = self.model.objects.filter(**lookup)
        days_count = sum(len(week) for week in days)
        FormClass = forms.modelformset_factory(self.model, self.form_class, extra=days_count)
        if self.request.method == 'POST':
            formset = self.month_formset = FormClass(self.request.POST, queryset=queryset)
        else:
            formset = self.month_formset = FormClass(queryset=queryset)

        # {1日のdatetime: 1日に関連するフォーム, 2日のdatetime: 2日のフォーム...}のような辞書を作る
        day_forms = {day: [] for week in days for day in week}

        # 各日に、新規作成用フォームを1つずつ配置
        for empty_form, (date, empty_list) in zip(formset.extra_forms, day_forms.items()):
            empty_form.initial = {self.date_field: date}
            empty_list.append(empty_form)

        # スケジュールがある各日に、そのスケジュールの更新用フォームを配置
        for bound_form in formset.initial_forms:
            instance = bound_form.instance
            date = getattr(instance, self.date_field)
            day_forms[date].append(bound_form)

        # day_forms辞書を、周毎に分割する。[{1日: 1日のフォーム...}, {8日: 8日のフォーム...}, ...]
        # 7個ずつ取り出して分割しています。
        return [{key: day_forms[key] for key in itertools.islice(day_forms, i, i+7)} for i in range(0, days_count, 7)]

    def get_month_calendar(self):
        calendar_context = super().get_month_calendar()
        month_days = calendar_context['month_days']
        month_first = month_days[0][0]
        month_last = month_days[-1][-1]
        calendar_context['month_day_forms'] = self.get_month_forms(
            month_first,
            month_last,
            month_days
        )
        calendar_context['month_formset'] = self.month_formset
        return calendar_context
