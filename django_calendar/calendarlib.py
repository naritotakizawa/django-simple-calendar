"""カレンダーを作成するためのモジュール."""
from calendar import month_name, monthrange, LocaleHTMLCalendar
import datetime
from django.utils import timezone
from django.shortcuts import resolve_url
from .models import Schedule

DAY_HTML = """\
<td class="{css_class}">
    <a href="javascript:void(0);" \
    onclick="window.open('{open_url}','subwin','width=500,height=500');">
        {day}
    </a>
    {schedule_html}
</td>
"""

SCHEDULE_LINK_AND_NUM = """\
<a href="{schedule_link}">
    <span class="badge badge-primary">+{schedule_num}</span>
</a>
"""


def create_day_html(year, month, day, css_class):
    """カレンダーの日付部分のhtmlを作成する.

    引数:
        year: 年
        month: 月
        day: 日
        css_class: 日付部分のhtmlに与えたいcssのクラス

    返り値:
        日付部分のhtml。具体的にはDAY_HTMLに変数を埋め込んだ文字列

    """
    date = datetime.datetime(
        year=year, month=month, day=day
    )
    all_count = Schedule.objects.filter(
        date=timezone.make_aware(date)
    ).count()
    if all_count:
        schedule_link_and_num = SCHEDULE_LINK_AND_NUM.format(
            schedule_link=resolve_url(
                'django_calendar:schedule_list',
                year=year, month=month, day=day
            ),
            schedule_num=all_count
        )
    else:
        schedule_link_and_num = ''

    return DAY_HTML.format(
        css_class=css_class,
        open_url=resolve_url('django_calendar:schedule_create',
                             year=year, month=month, day=day),
        day=day,
        schedule_html=schedule_link_and_num
    )


def prev_or_next_url(date, num, title):
    """前月、次月へのリンクとなるhtmlを作成する.

    引数:
        date: datetime.datetimeオブジェクト。増減の基準となる日付を渡す
        num: 増減の数字。1月後は1、1月前は-1
        title: リンクとして表示される文字列。prev、next、前月、など

    返り値:
        '<a href={url}>{title}</a>'に変数を埋め込んだ文字列

    """

    date = add_months(date, num)
    url = resolve_url(
        'django_calendar:calendar',
        year=date.year,
        month=date.month,
    )
    return '<a href={url}>{title}</a>'.format(url=url, title=title)


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
    return timezone.make_aware(date)


def make_aware_date(year=None, month=None):
    """awareなdatetimeオブジェクトを作成する.

    年と月を受取り、awareなdatetimeオブジェクトを作成する yearとmonthがNoneの場合は、今日

    """
    if year is None and month is None:
        date = timezone.now()
    elif year and month:
        naive_date = datetime.datetime(year=int(year), month=int(month), day=1)
        date = timezone.make_aware(naive_date)
    return date


class Calendar(LocaleHTMLCalendar):

    def __init__(self, date, firstweekday=0, locale=None):
        super().__init__(firstweekday, locale)
        self.date = date

    def formatday(self, day, weekday):
        """tableタグの日付部分のhtmlを作成する<td>...</td>."""

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            day_html = create_day_html(
                self.date.year, self.date.month, day,
                self.cssclasses[weekday]
            )
            return day_html

    def formatmonthname(self, theyear, themonth, withyear=True):
        """tableタグの一番上、タイトル部分にあたるhtmlを作成する."""
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        prev_a_tag = prev_or_next_url(self.date, -1, 'prev')
        next_a_tag = prev_or_next_url(self.date, 1, 'next')
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
