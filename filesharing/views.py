# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from filesharing.models import *

from django.views.generic import ListView, TemplateView


class IndexView(TemplateView):
    template_name  = 'index.html'


#TODO: переделать
class FilesView(ListView):
    model = Directory
    context_object_name = "file_list"
    template_name = 'home.html'

    def __init__(self):
        #получаем текущую Директорию из всего пути
        self.cur_dir = Directory.objects.get_by_full_path(self.kwargs['full_path'])

    #добавляем список файлов в контекст для текущей директории
    def get_context_data(self, **kwargs):
        context = super(FilesView, self).get_context_data(**kwargs)
        context['files'] = File.objects.filter(parent=self.cur_dir)
        return context

    #получаем список директорий текущей директории
    def get_queryset(self):
        dirs = Directory.objects.filter(parent=self.cur_dir).filter(owner=self.request.user)
        return dirs