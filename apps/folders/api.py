# coding=utf-8

from rest_framework import viewsets, generics, mixins
from rest_framework.views import APIView, Response

from .models import Folder
from assets.models import Asset
from perms.utils import get_user_granted_assets
from users.permissions import IsValidUser, IsSuperUser
from common.utils import get_logger

logger = get_logger('folder.%s' % __name__)

class GetNode(APIView):
    permission_classes = (IsValidUser,)

    def get_granted_assets(self):
        queryset = get_user_granted_assets(self.request.user)
        return queryset

    def get_assets(self, parent_id, granted_assets):
        l = []

        # don't show the assets without parent
        if parent_id is None:
            return l

        assets = Asset.objects.filter(folder=parent_id)

        for asset in assets:
            if not self.request.user.is_superuser and asset not in granted_assets:
                continue

            d = {
                'id': '%s_%d' %(parent_id, asset.id),
                'text': asset.hostname,
                'type': 'file',
            }
            l.append(d)

        return l

    def get_children(self, parent):
        l = []
        nodes = parent.folder_set.all()
        for node in nodes:
            children = self.get_children(node) + self.get_assets(node)
            if len(children) == 0:
                continue

            d = {
                'id': str(node.id),
                'text': node.name,
                'children': children
            }
            l.append(d)
        return l

    def get_all_nodes(self):
        l = []
        nodes = Folder.objects.all()
        root_nodes = [node for node in nodes if not node.parent]
        for node in root_nodes:
            children = self.get_children(node) + self.get_assets(node)
            if not self.request.user.is_superuser and len(children) == 0:
                continue

            d = {
                'id': str(node.id),
                'text': node.name,
                'children': children
            }
            l.append(d)

        return l

    def check_child_granted_assets(self, folder, granted_assets):
        if len(granted_assets) == 0:
            return False

        # check assets
        children_assets = folder.asset_set.all()
        user_assets = [a for a in children_assets if a in granted_assets]
        if len(user_assets) > 0:
            return True

        # check folders
        children_folders = Folder.objects.filter(parent=folder.id)
        for folder in children_folders:
            if self.check_child_granted_assets(folder, granted_assets):
                return True

        return False

    def get_folders(self, parent_id, granted_assets):
        l = []
        folders = Folder.objects.filter(parent=parent_id)

        for folder in folders:
            if not self.request.user.is_superuser and not self.check_child_granted_assets(folder, granted_assets):
                continue

            d = {
                'id': str(folder.id),
                'text': folder.name,
                'children': True,
                'type': 'folder'
            }
            l.append(d)

        return l

    def get_node(self, node_id):
        l = []
        granted_assets = self.get_granted_assets()
        l += self.get_folders(node_id, granted_assets)
        l += self.get_assets(node_id, granted_assets)
        return l


    def get(self, request):
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
        nodes = [
            {
                "id":1,"text":"Root node","children":[
                    {"id":2,"text":"Child node 1","children":True},
                    {"id":3,"text":"Child node 2"}
                ]
            }
        ]
        '''
        nodes = None
        if 'lazy' in request.query_params:
            parent_id = request.query_params['id']
            if parent_id == '#':
                parent_id = None
            nodes = self.get_node(parent_id)
        else:
            nodes = self.get_all_nodes()

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
            'shell_types': self.get_available_shell_types(asset)
        }

        return asset_info

    def get_available_shell_types(self, asset):
        shell_types = []
        if asset.platform and asset.platform.lower() == 'windows':
            shell_types.append('RDP')
        elif asset.platform and asset.platform.lower() == 'linux':
            shell_types.append('XShell')
        else:
            logger.warning('W: unknown asset(%d) platform' % asset.id)

        return shell_types

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
