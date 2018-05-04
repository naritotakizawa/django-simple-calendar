======================
django-simple-calendar
======================

月間カレンダー、週間カレンダーなどの機能を提供します。

`解説ブログ <https://torina.top/detail/469>`_

確認した環境
----------

:Python: 3.6以上
:Django: 2.0以上


使い方
-----
1. インストールする。::

    git clone https://github.com/naritotakizawa/django-simple-calendar
    pip install django

2. 動かす。::

    python manage.py migrate
    python manage.py runserver

sampleappアプリケーションはサンプルです。月間カレンダー、週間カレンダー、スケジュール付き週間カレンダー、そして月間、週間、スケジュール登録のついたビューがあります。いずれ、pipでインストールできるようにパッケージングするかもしれません。私のモチベーションと興味が、再燃したら。