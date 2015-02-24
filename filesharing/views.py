# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages

from filesharing.models import *
from filesharing.forms import *

from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView


#переопределячем значение тэга сообщения под стиль бутстрапа, чтобы вместо error стал danger
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.ERROR: 'danger',}


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

    def get_initial(self):
        return {
            'owner': self.request.user,
            'parent': Directory.objects.get_by_full_path(self.kwargs['path'])
        }

    def form_valid(self, form):
        # получаем объект на основе данных формы
        instance = form.save(commit=False)

        # заполняем неполученные поля
        parent_path = self.kwargs['path']
        self.success_url = parent_path
        instance.parent = Directory.objects.get_by_full_path(parent_path)
        instance.owner = self.request.user

        if instance.parent.has_access(self.request.user):
            # назначаем владельца
            instance.owner = self.request.user

            # А теперь можно сохранить в базу
            instance.save()
            messages.add_message(self.request, messages.SUCCESS, 'Директория "' + instance.name + '" успешно создана' )
        else:
            messages.add_message(self.request, messages.ERROR, 'Вы не имеете право создавать директории в этой папке' )
        return super(DirCreate, self).form_valid(form)

    def form_invalid(self, form):
        return HttpResponse("form error")


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

    def prepare_dir_context(self, context):
        # список файлов и папок в текущей директории
        if not self.cur_dir.has_access(self.request.user):
            context['critical_error'] = self.errors['ACCESS_DENIED']
        else:
            context['files'] = File.objects.filter(parent=self.cur_dir)
            context['dirs'] = Directory.objects.filter(parent=self.cur_dir)

            # информация для навигации
            context.update(self.navigation_inform())

            context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
            context['UploadFileForm'] = self.get_form(UploadFileForm)
            context['UpdateDirectoryNameForm'] = self.get_form(UpdateDirectoryNameForm)
        return context

    def prepare_file_context(self, context):
        self.cur_dir = self.cur_file.parent
        if not self.cur_dir.has_access(self.request.user):
            context['critical_error'] = self.errors['ACCESS_DENIED']
        else:
            context['file'] = self.cur_file
            context.update(self.navigation_inform())

            # TODO: формы другие должны быть (переименования, удаления)
            context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
            context['UploadFileForm'] = self.get_form(UploadFileForm)
            context['UpdateDirectoryNameForm'] = self.get_form(
                UpdateDirectoryNameForm)


            # TODO: формы другие должны быть (переименования, удаления)
            context['CreateDirForm'] = self.get_form(CreateDirectoryForm)
            context['UploadFileForm'] = self.get_form(UploadFileForm)

        return context

    def get_context_data(self, **kwargs):
        path = self.kwargs['path']
        context = super(FilesView, self).get_context_data(**kwargs)
        context['messages'] = messages.get_messages(self.request)

        self.cur_dir = Directory.objects.get_by_full_path(path)
        if self.cur_dir:
            # если по запрошенному пути найдена папка
            context = self.prepare_dir_context(context)
        else:
            # если по запрошенному пати найден файл
            self.cur_file = File.objects.get_by_full_path(path)
            if self.cur_file:
                context = self.prepare_file_context(context)
            else:
                context['critical_error'] = self.errors['BAD_PATH']

        return context
