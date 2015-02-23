# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages

from filesharing.models import *
from filesharing.forms import *

from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView


<<<<<<< HEAD

#переопределячем значение тэга сообщения под стиль бутстрапа, чтобы вместо error стал danger
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.ERROR: 'danger',}


=======
>>>>>>> 8c7bf9f0a841f9d45ca0d996988cf570f622a26e
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

        if instance.parent.has_access(self.request.user):
            # А теперь можно сохранить в базу
            instance.save()
            messages.add_message(self.request, messages.SUCCESS, 'Файл "' + instance.name.encode('utf-8') + '" был успешно загружен' )
        else:
            messages.add_message(self.request, messages.ERROR, 'Вы не имеете право загружать файлы в данную директорию' )
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
        #получаем будущего родителя
        instance.parent = Directory.objects.get_by_full_path(my_parent_path)

        if instance.parent.has_access(self.request.user):
            # назначаем владельца
            instance.owner = self.request.user

            # А теперь можно сохранить в базу
            instance.save()
            messages.add_message(self.request, messages.SUCCESS, 'Директория "' + instance.name.encode('utf-8') + '" успешно создана' )
        else:
            messages.add_message(self.request, messages.ERROR, 'Вы не имеете право создавать директории в этой папке' )

        return HttpResponseRedirect(self.success_url)


<<<<<<< HEAD
class DirUpdate(UpdateView):
    form_class = UpdateDirectoryNameForm
    model = Directory
    template_name = 'home.html'
    success_url = '/home/'
    slug_field = 'name'

    def get_object(self):
        return Directory.objects.get_by_full_path(self.kwargs['path'])

    def form_valid(self, form):
        #получаем родительскую директорию
        #my_parent_path = self.kwargs['path']

        # говорим, чтобы view не торопилас сохранять директорию
        instance = form.save(commit=False)

        if instance.has_access(self.request.user):
            instance.owner = self.request.user
            path = self.kwargs['path']
            path = path.rstrip('/')
            dirs_path, name = os.path.split(path)
            dir_before = self.get_object()
            # А теперь можно сохранить в базу
            instance.save()
            messages.add_message(self.request, messages.SUCCESS, 'Директория "' + dir_before.name.encode('utf-8') + '" успешно переименована в "' + instance.name.encode('utf-8') + '"')
        else:
            messages.add_message(self.request, messages.ERROR, 'Вы не имеете право изменять данную директорию' )

        return HttpResponseRedirect(dirs_path + '/' + instance.name)


class DirDelete(DeleteView):
    model = Directory
    template_name = 'home.html'
    success_url = '/home/'

    def get_object(self):
        return Directory.objects.get_by_full_path(self.kwargs['path'])

    def delete(self, request, *args, **kwargs):
        object = self.get_object()

        if object.has_access(self.request.user):
            object.delete()
            messages.add_message(self.request, messages.SUCCESS, 'Директория  была успешно удалена' )
        else:
            messages.add_message(self.request, messages.ERROR, 'Вы не имеете право удалять директории в этой папке' )

        path = self.kwargs['path']
        path = path.rstrip('/')
        dirs_path, name = os.path.split(path)

        return HttpResponseRedirect(dirs_path)

=======
>>>>>>> 8c7bf9f0a841f9d45ca0d996988cf570f622a26e
class FilesView(FormMixin, TemplateView):
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
            messages.add_message(self.request, messages.ERROR, 'Вам сюда доступ запрещён' )
            return dict()

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
            messages.add_message(self.request, messages.ERROR, 'Вам сюда доступ запрещён' )
            return dict()

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
        context['messages'] = messages.get_messages(self.request)

        if self.cur_dir:
            # если по запрошенному пути найдена папка

            # список файлов и папок в текущей директории
            context.update(self.list_dir())

            # информация для навигации
            context.update(self.navigation_inform())
<<<<<<< HEAD
            context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
            context['UploadFileForm'] = self.get_form(UploadFileForm)
            context['UpdateDirectoryNameForm'] = self.get_form(UpdateDirectoryNameForm)
=======

            context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
            context['UploadFileForm'] = self.get_form(UploadFileForm)
>>>>>>> 8c7bf9f0a841f9d45ca0d996988cf570f622a26e
            # TODO  формы удаления и переименования директории
        else:
            # если по запрошенному пати найден файл
            self.cur_file = File.objects.get_by_full_path(path)
            if self.cur_file:
                context.update(self.list_file())
                context.update(self.navigation_inform())
<<<<<<< HEAD
                # TODO: формы другие должны быть (переименования, удаления)
                context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
                context['UploadFileForm'] = self.get_form(UploadFileForm)
                context['UpdateDirectoryNameForm'] = self.get_form(UpdateDirectoryNameForm)
=======
>>>>>>> 8c7bf9f0a841f9d45ca0d996988cf570f622a26e

                # TODO: формы другие должны быть (переименования, удаления)
                context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
                context['UploadFileForm'] = self.get_form(UploadFileForm)
            else:
                messages.add_message(self.request, messages.ERROR, 'Такого пути не существует' )

        return context
