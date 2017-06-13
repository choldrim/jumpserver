# coding=utf-8

from django.conf.urls import url
from .. import api

app_name = 'api-extension'

urlpatterns = [
    url(r'^v1/check-update', api.CheckUpdate.as_view(), name='check-update'),
]
