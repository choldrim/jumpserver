# coding=utf-8

from django.conf.urls import url
from .. import views

app_name = 'folders'

urlpatterns = [
    url(r'^folder/list$', views.FolderListView.as_view(), name='folder-list'),
]
