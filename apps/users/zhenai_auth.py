# coding=utf-8
from __future__ import unicode_literals

import hashlib
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

from .models import User
from common.utils import get_logger

logger = get_logger(__name__)

class OAAuth(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def __init__(self):
        pass

    @staticmethod
    def check_with_OA(username, password):
        username = '%s@zhenai.com' % username
        m = hashlib.md5()
        mixed_pwd = password + 'ZAOA_LOGIN'
        m.update(mixed_pwd.encode())
        mixed_pwd = m.hexdigest()

        url = '%s/user/login' % (settings.OA_API_URL)
        d = {
            "username": username,
            "password": mixed_pwd
        }

        r = requests.post(url, data=d)
        if not r.ok:
            return False, 'OA server error'
        elif r.json().get('ret') != 0:
            return False, r.json().get('msg')
        else:
            return True, r.json().get('data')

    def _create_user(self, username, data):
        user = User(username=username, name=data.get('realname', ''), email=data.get('email', ''))
        user.save()
        logger.debug('Create new user: %s' % username)
        return user

    def _undecorate_username(self, username):
        if r'@zhenai.com' in username:
            username = username.split('@zhenai.com')[0]

        return username

    def authenticate(self, username=None, password=None, **kwargs):
        if username == 'admin':
            try:
                UserModel = get_user_model()
                user = UserModel._default_manager.get_by_natural_key(username)
                return user
            except UserModel.DoesNotExist:
                return None
        else:
            username = self._undecorate_username(username)
            login_valid, msg = OAAuth.check_with_OA(username, password)
            logger.debug('OA server reply: %s' % msg)

            if login_valid:
                data = msg
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = self._create_user(username, data)
                return user
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
