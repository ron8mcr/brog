# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from filesharing.models import *
from filesharing.forms import *

from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView


class IndexView(TemplateView):
    template_name = 'index.html'


# TODO: проверка пользователя, корректного именти и бла бла
class FileUpload(CreateView):
    form_class = UploadFileForm
    template_name = 'home.html'
    success_url = 'home'

    def form_valid(self, form):
        #получаем родительскую директорию
        my_parent_path = self.kwargs['path']
        self.success_url = my_parent_path

        # говорим, чтобы view не торопилас сохранять директорию
        instance = form.save(commit=False)

        #получаем будущего родителя
        instance.parent = Directory.objects.get_by_full_path(my_parent_path)

        # А теперь можно сохранить в базу
        instance.save()
        return HttpResponseRedirect(self.success_url)

# TODO: разобраться, что происходит в случае ошибки и как это обрабатывать
class DirCreate(CreateView):
    form_class = CreateDirectoryForm
    template_name = 'home.html'
    success_url = 'home'

    def form_valid(self, form):
        #получаем родительскую директорию
        my_parent_path = self.kwargs['path']
        self.success_url = my_parent_path

        # говорим, чтобы view не торопилас сохранять директорию
        instance = form.save(commit=False)

        # назначаем владельца
        instance.owner = self.request.user

        #получаем будущего родителя
        instance.parent = Directory.objects.get_by_full_path(my_parent_path)

        # А теперь можно сохранить в базу
        instance.save()
        return HttpResponseRedirect(self.success_url)


class FilesView(FormMixin, TemplateView):
    errors = {
        'BAD_PATH': "Введенный путь не существует",
        'ACCESS_DENIED': "Вам сюда доступ запрещён"
    }
    template_name = 'home.html'

    def navigation_inform(self):
        """
        :return:информация для полей навигации
        """
        result = dict()

        # папки, составляющие полный пусть (для СТРОКИ навигации)
        result['path_dirs'] = self.cur_dir.get_ancestors(
            include_self=True)

        # дерево папок пользователя - для ДЕРЕВА навигации
        result['user_dirs'] = self.request.user.home_directory.get_descendants(include_self=True)
        result['cur_dir'] = self.cur_dir
        return result

    def list_dir(self):
        """
        :return:Список файлов и директорий в запрошенной директории, если есть доступ
                или ошибку
        """
        if self.cur_dir.has_access(self.request.user):
            content = dict()
            content['files'] = File.objects.filter(parent=self.cur_dir)
            content['dirs'] = Directory.objects.filter(parent=self.cur_dir)
            return content
        else:
            return {'error': self.errors['ACCESS_DENIED']}

    def list_file(self):
        """
        :return:информация по запрошенному файлу или ошибка
        """
        result = dict()
        # родительская директория
        self.cur_dir = self.cur_file.parent

        if self.cur_file.has_access(self.request.user):
            return {'file': self.cur_file}
        else:
            return {'error': self.errors['ACCESS_DENIED']}

    def get_context_data(self, **kwargs):
        path = self.kwargs['path']
        context = super(FilesView, self).get_context_data(**kwargs)
        self.cur_dir = Directory.objects.get_by_full_path(path)
        if self.cur_dir:
            # если по запрошенному пути найдена папка

            # список файлов и папок в текущей директории
            context.update(self.list_dir())

            # информация для навигации
            context.update(self.navigation_inform())

            context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
            context['UploadFileForm'] = self.get_form(UploadFileForm)
            # TODO  формы удаления и переименования директории
        else:
            # если по запрошенному пати найден файл
            self.cur_file = File.objects.get_by_full_path(path)
            if self.cur_file:
                context.update(self.list_file())
                context.update(self.navigation_inform())

                # TODO: формы другие должны быть (переименования, удаления)
                context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
                context['UploadFileForm'] = self.get_form(UploadFileForm)
            else:
                context['error'] = self.errors['BAD_PATH']
        return context