======================
django-simple-calendar
======================
.. image:: https://travis-ci.org/naritotakizawa/django-simple-calendar.svg?branch=master
    :target: https://travis-ci.org/naritotakizawa/django-simple-calendar

.. image:: https://coveralls.io/repos/github/naritotakizawa/django-simple-calendar/badge.svg
    :target: https://coveralls.io/github/naritotakizawa/django-simple-calendar

カレンダーでスケジュールを登録していくサンプルアプリ


Requirement
--------------

:Python: 3.4以上
:Django: 1.9以上


Quick start
-----------
1. インストールする::

    pip install -U https://github.com/naritotakizawa/django-simple-calendar/archive/master.tar.gz

2. settings.pyのINSTALLED_APPSに足す::

    INSTALLED_APPS = [
        ...
        'django_calendar',  # add
    ]

3. ルートのurls.pyに足す::

	urlpatterns = [
	    url(r'^admin/', admin.site.urls),
	    url(r'^calendar/', include('django_calendar.urls')),  # add
	]

4. python manage.py migrate　でモデルを追加する.

5. python manage.py runserver で動かし、/calendarにアクセス