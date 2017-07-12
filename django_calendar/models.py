import datetime
from django.db import models
from django.utils import timezone


class Schedule(models.Model):
    """スケジュール."""

    memo = models.TextField('メモ')
    date = models.DateField('日付')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.memo


class WithTimeSchedule(models.Model):
    """時間付きスケジュール."""

    memo = models.TextField('メモ')
    start_time = models.TimeField('開始時間', default=datetime.time(7, 0, 0))
    end_time = models.TimeField('終了時間', default=datetime.time(7, 0, 0))
    date = models.DateField('日付')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.memo
