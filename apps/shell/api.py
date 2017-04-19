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

    def render_template(self, request, asset_id, content):
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

    def get_asset_name(self, asset_id):
        try:
            obj = Asset.objects.get(pk=int(asset_id))
            return obj
        except Asset.DoesNotExist:
            logger.debug('asset(%s) not found' % asset_id)
            return None

    def get(self, request, asset_id):
        ret = {} 

        # try to get asset's name
        asset = self.get_asset_name(asset_id)
        if asset is None:
            err = 'asset(%s) not found' % asset_id
            logger.error(err)
            ret['err'] = True
            ret['result'] = err
            return Response(ret, status=404)
        else:
            ret['asset_name'] = asset.hostname

        shell_type = request.query_params.get('shell_type')
        path_prefix = os.path.join(settings.MEDIA_ROOT, 'files/shell')
        if shell_type == 'XShell':
            session_path =  os.path.join(path_prefix, 'xshell_template.xsh')
        else:
            err = '''"%s" doesn't match any known shell''' % shell_type
            logger.error(err)
            ret['err'] = True
            ret['result'] = err
            return Response(ret, status=400)

        # read session file
        with open(session_path) as fp:
            session_data = fp.read()

        session_data = self.render_template(request, asset_id, session_data)

        ret['err'] = False
        ret['result'] = session_data
        return Response(ret)


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
