# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals, absolute_import

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class FolderListView(LoginRequiredMixin, TemplateView):
    template_name = 'folders/folder_list.html'

    def get_context_data(self, **kwargs):
        context = {}
        kwargs.update(context)
        return super(FolderListView, self).get_context_data(**kwargs)
