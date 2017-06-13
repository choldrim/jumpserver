# coding=utf-8

import os
from ConfigParser import ConfigParser

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class CheckUpdate(APIView):
    permission_classes = (AllowAny, )

    def get(self, request):
        ret = {}

        config_file = '%s/files/ext/update/config.ini' % (settings.MEDIA_ROOT)
        if not os.path.exists(config_file):
            ret['version'] = '0.0.1'
            ret['binary_URL'] = ''
        else:
            ret['version'], ret['binary_URL'] = self.get_update_info(config_file)

        return Response(ret)

    def get_update_info(self, config_file):
        conf = ConfigParser()
        conf.read(config_file)
        version = conf.get('default', 'version')
        binary_file = conf.get('default', 'URL')
        return version, binary_file
