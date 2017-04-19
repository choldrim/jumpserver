# coding=utf-8

from rest_framework import viewsets, generics, mixins
from rest_framework.views import APIView, Response

from users.permissions import IsValidUser, IsSuperUser
from assets.models import Asset
from .models import Folder

class GetNode(APIView):
    permission_classes = (IsValidUser,)

    def get_assets(self, parent):
        l = []
        assets = parent.asset_set.all()
        for asset in assets:
            d = {
                'id': '%d_%d' %(parent.id, asset.id),
                'text': asset.hostname,
                'type': 'file',
                'icon': 'jstree-file'
            }
            l.append(d)
        return l

    def get_children(self, parent):
        l = []
        nodes = parent.folder_set.all()
        for node in nodes:
            d = {
                'id': str(node.id),
                'text': node.name,
            }
            d['children'] = self.get_children(node)
            d['children'] += self.get_assets(node)
            l.append(d)
        return l

    def get_nodes(self):
        l = []
        nodes = Folder.objects.all()
        root_nodes = [node for node in nodes if not node.parent]
        for node in root_nodes:
            d = {
                'id': str(node.id),
                'text': node.name,
            }
            d['children'] = self.get_children(node)
            l.append(d)

        return l

    def get_node(self):
        nodes = self.get_nodes()
        return nodes

    def get(self, request, *args, **kwargs):
        '''
        nodes = [
            {
                "id":1,
                "text":"Root node",
                "children":[
                    {"id":2,"text":"Child node 1"},
                    {"id":3,"text":"Child node 2", "type": "file", "icon": "jstree-file"}
                ]
            },
            {
                "id":"2_1",
                "text":"Root node",
                "children":[
                    {"id":"2_2","text":"Child node 1"},
                    {"id":"2_3","text":"Child node 2", "children": False, "type": "file", "icon": "jstree-file"}
                ]
            }
        ]
        '''
        nodes = self.get_node()
        return Response(nodes)

class GetContent(APIView):
    permission_classes = (IsValidUser,)

    def get_asset_info(self, asset_id):
        asset = Asset.objects.filter(pk=int(asset_id))
        if len(asset) != 1:
            return {}

        asset = asset[0]

        asset_info = {
            'id': asset.id,
            'ip': asset.ip,
            'public_ip': asset.public_ip,
            'os': asset.os,
            'os_arch': asset.os_arch,
        }

        return asset_info

    def get(self, request):
        _id = request.query_params.get('id')
        if not _id:
            return Response('id not found in params', status=400)
        if '_' not in _id:
            # folder
            return Response('it a folder')
        asset_id = _id.split('_')[1]
        asset_info = self.get_asset_info(asset_id)
        return Response(asset_info)

class DeleteNode(APIView):
    permission_classes = (IsSuperUser,)

class CreateNode(APIView):
    permission_classes = (IsSuperUser,)

class RenameNode(APIView):
    permission_classes = (IsSuperUser,)

class MoveNode(APIView):
    permission_classes = (IsSuperUser,)
