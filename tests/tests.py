"""テストを行うモジュール."""
import datetime
from django.test import TestCase
from django.urls import reverse
from django_calendar.models import Schedule, WithTimeSchedule


class TestCalendar(TestCase):
    """Calendarのテストクラス."""

    def setUp(self):
        """初期化。モデルを3件作成する."""
        date = datetime.datetime(year=2010, month=7, day=10)
        Schedule.objects.create(memo='1', date=date)
        Schedule.objects.create(memo='2', date=date)
        Schedule.objects.create(memo='3', date=date)

    def test_calendar_get(self):
        """カレンダーページのテスト."""
        response = self.client.get(reverse('django_calendar:calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'next')
        self.assertContains(response, 'prev')
        self.assertNotContains(response, '+3')

    def test_calendar_get2(self):
        """スケジュールが追加された月のカレンダーページテスト"""

        response = self.client.get(reverse(
            'django_calendar:calendar', kwargs={'year': '2010', 'month': '7'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '+3')

    def test_weekcalendar_get(self):
        """週間カレンダーページのテスト."""
        kwargs = {'year': '2010', 'month': '7', 'week': '1'}
        response = self.client.get(
            reverse('django_calendar:week_calendar', kwargs=kwargs)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '★1')
        self.assertNotContains(response, '★2')
        self.assertNotContains(response, '★3')

    def test_weekcalendar_get2(self):
        """スケジュールが追加された週のカレンダーページテスト."""
        kwargs = {'year': '2010', 'month': '7', 'week': '2'}
        response = self.client.get(
            reverse('django_calendar:week_calendar', kwargs=kwargs)
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '★1')
        self.assertContains(response, '★2')
        self.assertContains(response, '★3')

    def test_schedule_create_get(self):
        """スケジュール作成ページのテスト"""

        response = self.client.get(reverse(
            'django_calendar:schedule_create',
            kwargs={'year': '2010', 'month': '7', 'day': '10'})
        )
        self.assertEqual(response.status_code, 200)

    def test_schedule_create_post(self):
        """スケジュール作成ページのテスト"""

        response = self.client.post(
            reverse(
                'django_calendar:schedule_create',
                kwargs={'year': '2010', 'month': '7', 'day': '10'}
            ),
            {'memo': 'add'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Schedule.objects.count(), 4)
        self.assertContains(response, 'window.close();')

    def test_schedule_list_get(self):
        """スケジュール一覧ページのテスト"""
        response = self.client.get(reverse(
            'django_calendar:schedule_list',
            kwargs={'year': '2010', 'month': '7', 'day': '10'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['schedule_list'].order_by('pk'),
            ['<Schedule: 1>', '<Schedule: 2>', '<Schedule: 3>']
        )


class TestWithTimeCalendar(TestCase):
    """WithTimeCalendarのテストクラス."""

    def setUp(self):
        """初期化。モデルを3件作成する."""
        date = datetime.datetime(year=2010, month=7, day=10)
        WithTimeSchedule.objects.create(
            memo='1', date=date,
            start_time=datetime.time(hour=7),
            end_time=datetime.time(hour=7, minute=30)
        )
        WithTimeSchedule.objects.create(
            memo='2', date=date,
            start_time=datetime.time(hour=8),
            end_time=datetime.time(hour=10)
        )
        WithTimeSchedule.objects.create(
            memo='3', date=date,
            start_time=datetime.time(hour=10),
            end_time=datetime.time(hour=12, minute=30)
        )

    def test_calendar_get(self):
        """カレンダーページのテスト."""
        response = self.client.get(reverse('django_calendar:withtime_calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'next')
        self.assertContains(response, 'prev')
        self.assertNotContains(response, '+3')

    def test_calendar_get2(self):
        """スケジュールが追加された月のカレンダーページテスト"""

        response = self.client.get(reverse(
            'django_calendar:withtime_calendar',
            kwargs={'year': '2010', 'month': '7'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '+3')

    def test_weekcalendar_get(self):
        """週間カレンダーページのテスト."""
        kwargs = {'year': '2010', 'month': '7', 'week': '1'}
        response = self.client.get(
            reverse('django_calendar:withtime_week_calendar', kwargs=kwargs)
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '7:00:00〜07:30:00<br>1')
        self.assertNotContains(response, '8:00:00〜10:00:00<br>2')
        self.assertNotContains(response, '10:00:00〜12:30:00<br>3')

    def test_weekcalendar_get2(self):
        """スケジュールが追加された週のカレンダーページテスト."""
        kwargs = {'year': '2010', 'month': '7', 'week': '2'}
        response = self.client.get(
            reverse('django_calendar:withtime_week_calendar', kwargs=kwargs)
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '7:00:00〜07:30:00<br>1')
        self.assertContains(response, '8:00:00〜10:00:00<br>2')
        self.assertContains(response, '10:00:00〜12:30:00<br>3')

    def test_schedule_create_get(self):
        """スケジュール作成ページのテスト"""

        response = self.client.get(reverse(
            'django_calendar:withtime_schedule_create',
            kwargs={'year': '2010', 'month': '7', 'day': '10'})
        )
        self.assertEqual(response.status_code, 200)

    def test_schedule_create_post(self):
        """スケジュール作成ページのテスト"""

        response = self.client.post(
            reverse(
                'django_calendar:withtime_schedule_create',
                kwargs={'year': '2010', 'month': '7', 'day': '10',}
            ),
            {
                'memo': 'add',
                'start_time': '15:00',
                'end_time': '16:00',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WithTimeSchedule.objects.count(), 4)
        self.assertContains(response, 'window.close();')

    def test_schedule_create_post_error1(self):
        """スケジュール作成ページのテスト(終了時間エラー1)"""

        response = self.client.post(
            reverse(
                'django_calendar:withtime_schedule_create',
                kwargs={'year': '2010', 'month': '7', 'day': '10',}
            ),
            {
                'memo': 'add',
                'start_time': '15:00',
                'end_time': '14:00',  # 終了時間が開始時間よりも短い
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WithTimeSchedule.objects.count(), 3)
        self.assertContains(
            response, '終了時間は、開始時間よりも後にしてください',
        )

    def test_schedule_create_post_error2(self):
        """スケジュール作成ページのテスト(終了時間エラー2)"""

        response = self.client.post(
            reverse(
                'django_calendar:withtime_schedule_create',
                kwargs={'year': '2010', 'month': '7', 'day': '10',}
            ),
            {
                'memo': 'add',
                'start_time': '15:00',
                'end_time': '15:00',  # 終了時間が開始時間と同じ
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WithTimeSchedule.objects.count(), 3)
        self.assertContains(
            response, '終了時間は、開始時間よりも後にしてください',
        )

    def test_schedule_list_get(self):
        """スケジュール一覧ページのテスト"""
        response = self.client.get(reverse(
            'django_calendar:withtime_schedule_list',
            kwargs={'year': '2010', 'month': '7', 'day': '10'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['withtimeschedule_list'].order_by('pk'),
            ['<WithTimeSchedule: 1>', '<WithTimeSchedule: 2>', '<WithTimeSchedule: 3>']
        )
        self.assertContains(response, '7:00:00〜07:30:00<br>1')
        self.assertContains(response, '8:00:00〜10:00:00<br>2')
        self.assertContains(response, '10:00:00〜12:30:00<br>3')