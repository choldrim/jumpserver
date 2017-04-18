#!/usr/bin/env python3
# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Folder(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Folder name'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True,
        null=True, verbose_name=_('Parent folder'),)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Folder')

