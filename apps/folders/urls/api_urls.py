# coding:utf-8
from django.conf.urls import url
from .. import api
from rest_framework import routers

app_name = 'api-folders'

urlpatterns = [
    url(r'^v1/operation/get_node$', api.GetNode.as_view(), name='get-node'),
    url(r'^v1/operation/get_content$', api.GetContent.as_view(), name='get-content'),
    url(r'^v1/operation/remove_node$', api.DeleteNode.as_view(), name='delete-node'),
    url(r'^v1/operation/create_node$', api.CreateNode.as_view(), name='create-node'),
    url(r'^v1/operation/rename_node$', api.RenameNode.as_view(), name='rename-node'),
    url(r'^v1/operation/move_node$', api.MoveNode.as_view(), name='move-node'),
]
