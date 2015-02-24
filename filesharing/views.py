# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView

from filesharing.models import *
from filesharing.forms import *


# переопределячем значение тэга сообщения под стиль бутстрапа, чтобы вместо error стал danger
from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {message_constants.ERROR: 'danger', }


class IndexView(TemplateView):
    template_name = 'index.html'


class FilesView(FormMixin, TemplateView):
    errors = {
        'BAD_PATH': "Введенный путь не существует",
        'ACCESS_DENIED': "Вам сюда доступ запрещён"
    }
    template_name = 'filesharing/home.html'

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
        result['parent'] = self.cur_dir.parent
        return result

    def prepare_dir_context(self, context):
        # список файлов и папок в текущей директории
        if not self.cur_dir.has_access(self.request.user):
            context['error'] = self.errors['ACCESS_DENIED']
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
            context['error'] = self.errors['ACCESS_DENIED']
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
                context['error'] = self.errors['BAD_PATH']

        return context

    def post(self, request, *args, **kwargs):
        forms = {
            'create_dir':
                {'class': CreateDirectoryForm, 'handler': self.form_new_dir},
            'rename_dir':
                {'class': UpdateDirectoryNameForm, 'handler': self.form_rename_dir},
            'delete_dir':
                {'class': DeleteDirectoryForm, 'handler': self.form_remove_dir},
            'upload_file':
                {'class': UploadFileForm, 'handler': self.form_upload_file},
            'delete_file':
                {'class': DeleteFileForm, 'handler': self.form_delete_file}
        }
        print(self.request.POST)
        for form_name in forms:
            if form_name in self.request.POST:
                self.context = self.get_context_data(request=self.request)
                form_class = forms[form_name]['class']
                form = self.get_form(form_class)
                if form.is_valid():
                    return forms[form_name]['handler'](form)
                return render(self.request, 'filesharing/home.html', self.context)

    def form_new_dir(self, form):
        my_parent_path = self.kwargs['path']

        # говорим, чтобы view не торопилась сохранять директорию
        new_dir = form.save(commit=False)

        #получаем будущего родителя
        new_dir.parent = Directory.objects.get_by_full_path(
            my_parent_path)

        if new_dir.parent.has_access(self.request.user):
            # назначаем владельца
            new_dir.owner = self.request.user

            # А теперь можно сохранить в базу
            try:
                new_dir.save()
                messages.add_message(self.request, messages.SUCCESS,
                                     'Директория "' + new_dir.name
                                     + '" успешно создана')
            except IntegrityError as err:
                messages.add_message(self.request, messages.ERROR,
                                     "В одной директории не может быть файла и "
                                     "директории с одинаковыми именами")
        else:
            messages.add_message(self.request, messages.ERROR,
                                 'Вы не имеете право создавать директории в этой папке')
        return render(self.request, 'filesharing/home.html', self.context)

    def form_rename_dir(self, form):
        for_rename = Directory.objects.get_by_full_path(self.kwargs['path'])
        old_name = for_rename.name
        form = UpdateDirectoryNameForm(self.request.POST, instance=for_rename)

        if form.is_valid():
            instance = form.save(commit=False)

            if instance.has_access(self.request.user) and \
                            for_rename not in Directory.objects.root_nodes():

                # А теперь можно сохранить в базу
                instance.save()
                messages.add_message(self.request, messages.SUCCESS,
                                     'Директория "' + old_name +
                                     '" успешно переименована в "' + instance.name + '"')
                return HttpResponseRedirect(instance.full_path)
            else:
                messages.add_message(self.request, messages.ERROR, 'Вы не имеете право изменять данную директорию')
        return render(self.request, 'filesharing/home.html', self.context)

    def form_remove_dir(self, form):
        for_delete = Directory.objects.get_by_full_path(self.kwargs['path'])
        parent = for_delete.parent
        if for_delete.has_access(self.request.user) and for_delete not in Directory.objects.root_nodes():
            for_delete.delete()
            messages.add_message(self.request, messages.SUCCESS, 'Директория  была успешно удалена')
            return HttpResponseRedirect(parent.full_path)
        else:
            messages.add_message(self.request, messages.ERROR, 'Вы не имеете право удалять данную директорию')
        return render(self.request, 'filesharing/home.html', self.context)

    def form_upload_file(self, form):
        instance = form.save(commit=False)
        #получаем будущего родителя
        instance.parent = Directory.objects.get_by_full_path(self.kwargs['path'])

        if instance.parent.has_access(self.request.user):
            # А теперь можно сохранить в базу
            instance.save()
            messages.add_message(self.request, messages.SUCCESS, 'Файл "' + instance.name + '" был успешно загружен')
        else:
            messages.add_message(self.request, messages.ERROR, 'Вы не имеете право загружать файлы в данную директорию')
        return HttpResponseRedirect(instance.parent.full_path)

    def form_delete_file(self, form):
        for_delete = File.objects.get_by_full_path(self.kwargs['path'])
        parent = for_delete.parent
        if parent.has_access(self.request.user):
            for_delete.delete()
            messages.add_message(self.request, messages.SUCCESS, 'Файл был успешно удален')
            return HttpResponseRedirect(parent.full_path)
        else:
            messages.add_message(self.request, messages.ERROR, 'Вы не имеете право удалять данный файл')
        return render(self.request, 'filesharing/home.html', self.context)
