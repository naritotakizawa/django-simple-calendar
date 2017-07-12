"""カレンダーを作成するためのモジュール."""
from calendar import month_name, monthrange, LocaleHTMLCalendar
import datetime
from django.shortcuts import resolve_url

DAY_HTML = """
<td class="{css_class}">
    <a href="javascript:void(0);"
    onclick="window.open('{open_url}','subwin','width=500,height=500');">
        {day}
    </a>
    {schedule_html}
</td>
"""

SCHEDULE_LINK_AND_NUM = """
<a href="{schedule_link}">
    <span class="badge badge-primary">+{schedule_num}</span>
</a>
"""


def add_months(date, num):
    """datetimeオブジェクトに月を加算・減算する.

    引数:
        date: datetime.datetimeオブジェクト。増減の基準となる日付を渡す
        num: 増減の数字。1月後は1、1月前は-1

    返り値:
        n月後、n月前のawareなdatetimeオブジェクト

    """
    month = date.month - 1 + num
    year = int(date.year + month / 12)
    month = month % 12 + 1
    day = min(date.day, monthrange(year, month)[1])
    date = datetime.datetime(year=year, month=month, day=day)
    return date


class SimpleCalendarBS4(LocaleHTMLCalendar):
    """Bootstrap4対応したカスタムカレンダー."""

    def __init__(self, date, counter, firstweekday=0, locale=None):
        super().__init__(firstweekday, locale)
        self.date = date
        self.counter = counter

    def get_calendar_url(self, date):
        """現在利用しているカレンダーページのURLを返す."""
        return resolve_url(
            'django_calendar:calendar',
            year=date.year, month=date.month,
        )

    def get_schedule_create_url(self, year, month, day):
        """スケジュール作成ページのURLを返す."""
        return resolve_url(
            'django_calendar:schedule_create',
            year=year, month=month, day=day,
        )

    def get_schedule_list_url(self, year, month, day):
        """スケジュール一覧ページのURLを返す."""
        return resolve_url(
            'django_calendar:schedule_list',
            year=year, month=month, day=day,
        )

    def prev_or_next_url(self, date, num, title):
        """前月、次月へのリンクとなるhtmlを作成する.

        引数:
            date: datetime.datetimeオブジェクト。増減の基準となる日付を渡す
            num: 増減の数字。1月後は1、1月前は-1
            title: リンクとして表示される文字列。prev、next、前月、など

        返り値:
            '<a href={url}>{title}</a>'に変数を埋め込んだ文字列

        """
        date = add_months(date, num)
        return '<a href="{0}">{1}</a>'.format(
            self.get_calendar_url(date), title
        )

    def create_day_html(self, year, month, day, css_class, counter):
        """カレンダーの日付部分のhtmlを作成する.

        引数:
            year: 年
            month: 月
            day: 日
            css_class: 日付部分のhtmlに与えたいcssのクラス
            counter: {日付:スケジュール件数} な辞書

        返り値:
            日付部分のhtml。具体的にはDAY_HTMLに変数を埋め込んだ文字列

        """
        day_schedule_count = counter.get(day)
        if day_schedule_count:
            schedule_link_and_num = SCHEDULE_LINK_AND_NUM.format(
                schedule_link=self.get_schedule_list_url(year, month, day),
                schedule_num=day_schedule_count
            )
        else:
            schedule_link_and_num = ''

        return DAY_HTML.format(
            css_class=css_class,
            open_url=self.get_schedule_create_url(year, month, day),
            day=day,
            schedule_html=schedule_link_and_num
        )

    def formatday(self, day, weekday):
        """tableタグの日付部分のhtmlを作成する<td>...</td>."""
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            day_html = self.create_day_html(
                self.date.year, self.date.month, day,
                self.cssclasses[weekday], self.counter
            )
            return day_html

    def formatmonthname(self, theyear, themonth, withyear=True):
        """tableタグの一番上、タイトル部分にあたるhtmlを作成する."""
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        prev_a_tag = self.prev_or_next_url(self.date, -1, 'prev')
        next_a_tag = self.prev_or_next_url(self.date, 1, 'next')
        return '<tr><th colspan="7" class="month">{} {} {}</th></tr>'.format(
            prev_a_tag, s, next_a_tag
        )

    def formatmonth(self, theyear=None, themonth=None, withyear=True):
        """月のカレンダーを作成する."""
        if theyear is None:
            theyear = self.date.year
        if themonth is None:
            themonth = self.date.month
        v = []
        a = v.append
        a('<table class="month table">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


class WithTimeCalendarBS4(SimpleCalendarBS4):
    """Bootstrap4対応した時間付きカレンダー."""

    def get_calendar_url(self, date):
        """現在利用しているカレンダーページのURLを返す."""
        return resolve_url(
            'django_calendar:withtime_calendar',
            year=date.year, month=date.month,
        )

    def get_schedule_create_url(self, year, month, day):
        """スケジュール作成ページのURLを返す."""
        return resolve_url(
            'django_calendar:withtime_schedule_create',
            year=year, month=month, day=day,
        )

    def get_schedule_list_url(self, year, month, day):
        """スケジュール一覧ページのURLを返す."""
        return resolve_url(
            'django_calendar:withtime_schedule_list',
            year=year, month=month, day=day,
        )


class TimeScheduleBS4:
    """タイムスケジュールを作成する(Bootstrap4)."""

    def __init__(
        self, minute_height=1, hours=None, schedule_color='bg-info', step=1
    ):
        """初期化.

        引数:
        minute_height: 1分の高さ(px)。1ならば1時間が60px、全体で1440px
        hours: スケジュールに記載する時間の幅。range(6, 13)だと6〜12時まで
        schedule_color: スケジュールがある場合の背景色
        step: 何分毎にdivタグを入れるか。デフォルトは1分毎に1divタグ
              1に近いほどdivタグが多くなりパフォーマンスが落ちるが、細かい時間
              でも色をつけることができる

        """
        # hoursがNoneなら0から23時で
        if hours is None:
            self.hours = [x for x in range(24)]
        else:
            self.hours = hours
        self.step = step
        self.minute_height = minute_height
        self.hour_height = self.minute_height * 60
        self.max_height = self.hour_height * len(self.hours)
        self.schedule_color = schedule_color

    def convert(self, obj):
        """(開始時間、終了時間、スケジュールテキスト)のタプルを返す.

        format_schedueメソッドに渡した各scheduleオブジェクトを
        (開始時間, 終了時間,テキスト)の形に変換するためのメソッド
        return obj.start, obj.end, obj.text
        return obj['start'], obj['end'], obj['title']+obj['text']
        のようにしてください

        """
        message = '{}〜{}<br>{}'.format(
            obj.start_time, obj.end_time, obj.memo
        )
        return obj.start_time, obj.end_time, message

    def format_hour_name(self, hour):
        """左側の列、時間表示部分の作成."""
        div = '<div style="height:{0}px;" class="hour-name">{1}:00</div>'
        return div.format(self.hour_height, hour)

    def format_minute(self, schedule, now):
        """分部分の作成."""
        start, end, text = self.convert(schedule)
        context = {
            'color': self.schedule_color,
            'height': self.minute_height * self.step,
            'just-hour': '',
            'text': text,
        }
        # 1:00、2:00などの0分に枠線を入れるためのcss
        if now.minute == 0:
            context['just-hour'] = 'just-hour'

        # 現在ループの時間が開始時間〜終了時間内なら、色をつける
        if start <= now < end:

            # 既にtooltipを入れているなら背景色だけ
            if self.already_tooltip:
                base_html = (
                    '<div class="{color} {just-hour}" '
                    'style="height:{height}px;"></div>'
                )

            # 最初の予定なら、tooltipをつけてフラグをTrueに
            else:
                self.already_tooltip = True
                base_html = (
                    '<div class="{color} {just-hour}" '
                    'style="height:{height}px;" '
                    'data-html="true" title="{text}" data-placement="top" '
                    'data-trigger="manual"  data-toggle="tooltip">'
                    '</div>'
                )

        else:
            base_html = (
                '<div class="{just-hour}" style="height:{height}px;"></div>'
            )

        return base_html.format_map(context)

    def format_schedule(self, schedules):
        """タイムスケジュールを作成する."""
        v = []
        a = v.append
        a('<div class="row no-gutters">')

        # 左列、時間表示部分の作成
        a('<div class="col" style="height:{0}px;">'.format(self.max_height))
        for hour in self.hours:
            a(self.format_hour_name(hour))
        a('</div>')

        # 右列、スケジュール作成部分
        for schedule in schedules:
            # 予定の最初のdivタグにtooltipを導入するためのフラグ
            self.already_tooltip = False
            a('<div class="col minute-wrapper" style="height:{0}px;">'.format(
                self.max_height
            ))
            for hour in self.hours:
                for minute in range(0, 60, self.step):
                    now = datetime.time(hour=hour, minute=minute)
                    a(self.format_minute(schedule, now))
            a('</div>')

        a('</div>')

        return ''.join(v)
