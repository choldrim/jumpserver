# coding=utf-8

from django.conf.urls import url
from .. import api

app_name = 'shell'

urlpatterns = [
    url(r'^v1/session-file/(?P<asset_id>[0-9]+)/', api.SessionFile.as_view(), name='session-file'),
]
