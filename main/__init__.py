from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app
from . import mysql_setup

__all__ = ('celery_app',)
