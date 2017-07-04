"""テストを行うモジュール."""
from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_calendar.models import Schedule


class TestViews(TestCase):
    """Viewのテストクラス."""

    def setUp(self):
        """初期化。モデルを3件作成する."""
        date = datetime(year=2010, month=7, day=10)
        date = timezone.make_aware(date)
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