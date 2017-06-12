# coding=utf-8

import os
import base64
import json

from django.conf import settings
from django.template import Context, Template
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.utils import generate_token
from users.permissions import IsValidUser
from common.utils import get_logger
from assets.models import Asset


logger = get_logger(__name__)

class SessionFile(APIView):
    permission_classes = (IsValidUser,)

    def get(self, request, asset_id):
        ret = {} 

        # try to get asset's name
        asset = get_object_or_404(Asset, id=asset_id)
        shell_type = request.query_params.get('shell_type')
        if shell_type == 'XShell':
            session_data = self.get_xshell_session_file_data(request, asset)
        elif shell_type == 'RDP':
            session_data = self.get_rdp_session_file_data(request, asset)
            sys_users = asset.system_users.all()
            if len(sys_users) == 0:
                err = 'system users not set'
                logger.error(err)
                raise Exception(err)

            sys_user = sys_users[0] 
            ret['password'] = sys_user.password

        else:
            err = '''"%s" doesn't match any known shell''' % shell_type
            logger.error(err)
            ret['err'] = True
            ret['result'] = err
            return Response(ret, status=400)

        ret['err'] = False
        ret['result'] = session_data
        ret['asset_name'] = asset.hostname

        return Response(ret)

    def render_xshell_template(self, request, asset_id, content):
        template = Template(content)
        token = generate_token(request, request.user)
        c = Context({
            'coco_server': settings.SHELL_SERVER,
            'coco_port': settings.SHELL_PORT,
            'asset_id': asset_id,
            'token': token,
            'username': request.user.username,
        })
        return template.render(c)

    def get_xshell_session_file_data(self, request, asset):
        path_prefix = os.path.join(settings.MEDIA_ROOT, 'files/shell')
        session_path = os.path.join(path_prefix, 'xshell_template.xsh')

        # read session file
        with open(session_path) as fp:
            session_data = fp.read()

        session_data = self.render_xshell_template(request, asset.id, session_data)
        return session_data

    def render_rdp_template(self, request, asset, content):
        template = Template(content)
        token = generate_token(request, request.user)
        sys_users = asset.system_users.all()
        if len(sys_users) == 0:
            err = 'system users not set'
            logger.error(err)
            raise Exception(err)

        sys_user = sys_users[0] 
        c = Context({
            'full_address': '%s:%s' % (asset.ip, asset.port),
            'username': sys_user.username,
        })
        return template.render(c)

    def get_rdp_session_file_data(self, request, asset):
        path_prefix = os.path.join(settings.MEDIA_ROOT, 'files/shell')
        session_path = os.path.join(path_prefix, 'rdp_template.rdp')

        # read session file
        with open(session_path) as fp:
            session_data = fp.read()

        session_data = self.render_rdp_template(request, asset, session_data)
        return session_data


class URLSchema(APIView):
    permission_classes = (IsValidUser,)

    def get(self, request):
        asset_id = request.query_params.get('asset_id')
        asset_id = int(asset_id)
        shell_type = request.query_params.get('shell_type')
        if None in [asset_id, shell_type]:
            ret = {
                'message': _('Params not correct')
            }
            return Response(ret, status=400)

        d = {
            'token': generate_token(request, request.user),
            'asset_id': asset_id,
            'shell_type': shell_type,
        }
        logger.debug('get url-schema with object: %s' % json.dumps(d))
        s = json.dumps(d)
        binary = base64.b64encode(s.encode())
        url = binary.decode()
        logger.debug('url-schema url: %s' % url)
        ret = {
            'url': url
        }
        return Response(ret)
