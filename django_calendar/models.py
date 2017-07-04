from django.db import models
from django.utils import timezone


class Schedule(models.Model):
    """スケジュール."""

    memo = models.TextField('メモ')
    date = models.DateField('日付')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.memo
