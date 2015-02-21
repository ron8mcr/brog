# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from filesharing.models import *

from django.views.generic import DetailView, TemplateView


class IndexView(TemplateView):
    template_name  = 'index.html'


#TODO: переделать
class FilesView(TemplateView):
    errors = {
        'BAD_PATH': "Введенный путь не существует",
        'ACCESS_DENIED': "Вам сюда доступ запрещён"
    }
    template_name = 'home.html'

    def list_dir(self):
        """
        :return:Список файлов и директорий в запрошенной директории, если есть доступ
                или ошибку
        """
        if self.cur_dir.has_access(self.request.user):
            content = dict()
            content['files'] = File.objects.filter(parent=self.cur_dir)
            content['dirs'] = Directory.objects.filter(parent=self.cur_dir)
            content['parent'] = self.cur_dir.parent
            return content
        else:
            return {'error': self.errors['ACCESS_DENIED']}

    def get_context_data(self, **kwargs):
        path = self.kwargs['path']
        context = super(FilesView, self).get_context_data(**kwargs)

        self.cur_dir = Directory.objects.get_by_full_path(path)
        if self.cur_dir:
            context.update(self.list_dir())
        else:
            self.cur_file = File.objects.get_by_full_path(path)
            if self.cur_file:
                # TODO: что же делать, если запрошен файл? redirect?
                if self.cur_file.has_access(self.request.user):
                    context['file'] = self.cur_file
                else:
                    context['error'] = self.errors['ACCESS_DENIED']

            else:
                context['error'] = self.errors['BAD_PATH']
        return context