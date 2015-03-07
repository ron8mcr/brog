# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from filesharing.models import Directory, File
from filesharing.forms import CreateDirectoryForm, UploadFileForm, UpdateDirectoryNameForm
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView
from sendfile import sendfile
from rest_framework.authtoken.models import Token


class AddFieldsMixin(object):
    """ Миксин для добавления дополнительных полей в экземпляр
    И дополнительных проверок, например, на права доступа
    """
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        try:
            # если появились какие-либо ошибки при добавлении полей в форму,
            # метод сам должен записать эти ошибки и бросить исключение
            form = self.add_fields(form)
        except ValidationError as err:
            return self.form_invalid(form)
        self.additional_checks(form)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def add_fields(self, form):
        return form

    def additional_checks(self, form):
        pass


class FormErrorMessagesMixin(object):
    def form_invalid(self, form):
        for err_type in form.errors:
            for err in form.errors[err_type]:
                messages.add_message(self.request, messages.ERROR, err)
        return HttpResponseRedirect(self.kwargs['path'])


class DirCreate(AddFieldsMixin, FormErrorMessagesMixin, CreateView):
    template_name = 'home.html'
    form_class = CreateDirectoryForm

    def add_fields(self, form):
        form.instance.owner = self.request.user
        try:
            form.instance.parent = Directory.objects.get_by_full_path(
                self.kwargs['path'])
        except Directory.DoesNotExist:
            form.add_error(None, "Неверный путь")
            raise ValidationError
        return form

    def additional_checks(self, form):
        if not form.instance.parent.has_access(self.request.user):
            form.add_error(None, "Вы не имеете прав доступа к данной директории!")

    def form_valid(self, form):
        self.success_url = self.kwargs['path']
        messages.add_message(self.request, messages.SUCCESS,
                             "Директория \"{}\" успешно cоздана".format(form.instance.name))
        return super(DirCreate, self).form_valid(form)


class FileUpload(AddFieldsMixin, FormErrorMessagesMixin, CreateView):
    template_name = 'home.html'
    form_class = UploadFileForm

    def add_fields(self, form):
        try:
            form.instance.parent = Directory.objects.get_by_full_path(
                self.kwargs['path'])
        except Directory.DoesNotExist:
            form.add_error(None, "Неверный путь")
            raise ValidationError
        return form

    def additional_checks(self, form):
        if not form.instance.parent.has_access(self.request.user):
            form.add_error(None, "Вы не имеете прав доступа к данной директории!")

    def form_valid(self, form):
        self.success_url = self.kwargs['path']
        messages.add_message(self.request, messages.SUCCESS,
                             "Файл \"{}\" успешно загружен".format(form.instance.name))
        return super(FileUpload, self).form_valid(form)


class DirUpdate(AddFieldsMixin, FormErrorMessagesMixin, UpdateView):
    form_class = UpdateDirectoryNameForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(DirUpdate, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Directory.objects.get_by_full_path(self.kwargs['path'])

    def additional_checks(self, form):
        for_rename = self.get_object()
        if for_rename in Directory.objects.root_nodes():
            form.add_error(None, "Невозможно переименовать домашнюю директорию")
            return
        if not for_rename.has_access(self.request.user):
            form.add_error(None, "Вы не имеете прав доступа к данной директории!")

    def form_valid(self, form):
        for_rename = self.get_object()
        instance = form.save(commit=False)
        instance.save()
        messages.add_message(self.request, messages.SUCCESS,
                             "Директория \"{}\" успешно переименована в \"{}\"".format(
                                 for_rename.name, instance.name))
        return HttpResponseRedirect(instance.full_path)


class DirDelete(DeleteView):
    model = Directory

    def get_object(self, queryset=None):
        return Directory.objects.get_by_full_path(self.kwargs['path'])

    def delete(self, request, *args, **kwargs):
        dir_for_del = self.get_object()
        try:
            parent_path = dir_for_del.parent.full_path
        except AttributeError:
            messages.add_message(self.request, messages.ERROR,
                                 "Вы не имеете право удалять домашнюю директорию")
            return HttpResponseRedirect(dir_for_del.full_path)

        if dir_for_del.has_access(self.request.user):
            dir_for_del.delete()
            messages.add_message(self.request, messages.SUCCESS,
                                 "Директория была успешно удалена")
        else:
            messages.add_message(self.request, messages.ERROR,
                                 "Вы не имеете право удалять данную директорию")
        return HttpResponseRedirect(parent_path)


class FilesView(FormMixin, TemplateView):
    errors = {
        'BAD_PATH': "Введенный путь не существует",
        'ACCESS_DENIED': "Вам сюда доступ запрещён"
    }
    template_name = 'home.html'

    def navigation_inform(self, cur_dir):
        """
        :return:информация для полей навигации
        """
        return {
            # папки, составляющие полный пусть (для СТРОКИ навигации)
            'path_dirs': cur_dir.get_ancestors(include_self=True),
            # дерево папок пользователя - для ДЕРЕВА навигации
            'user_dirs': self.request.user.home_directory.get_descendants(
                include_self=True),
            'cur_dir': cur_dir
        }

    def prepare_dir_context(self, cur_dir):
        # список файлов и папок в текущей директории
        if not cur_dir.has_access(self.request.user):
            return {'critical_error': self.errors['ACCESS_DENIED']}
        else:
            result = {
                'files': File.objects.filter(parent=cur_dir),
                'dirs': Directory.objects.filter(parent=cur_dir),
                'CreateDirForm': CreateDirectoryForm,
                'UploadFileForm': UploadFileForm,
                'UpdateDirectoryNameForm': UpdateDirectoryNameForm,
            }
            result.update(self.navigation_inform(cur_dir))
            return result

    def prepare_file_context(self, cur_file):
        if not cur_file.has_access(self.request.user):
            return {'critical_error': self.errors['ACCESS_DENIED']}
        else:
            result = {'file': cur_file}
            result.update(self.navigation_inform(cur_file.parent))
            return result

    def get_context_data(self, **kwargs):
        path = self.kwargs['path']
        context = super(FilesView, self).get_context_data(**kwargs)
        context['messages'] = messages.get_messages(self.request)
        context['token'] = Token.objects.get(user=self.request.user).key

        try:
            context.update(self.prepare_dir_context(
                Directory.objects.get_by_full_path(path)))
        except Directory.DoesNotExist:
            try:
                context.update(self.prepare_file_context(
                    File.objects.get_by_full_path(path)))
            except (Directory.DoesNotExist, File.DoesNotExist):
                context['critical_error'] = self.errors['BAD_PATH']

        return context

    def render_to_response(self, context):
        if 'file' in context:
            for_send = context['file']
            return sendfile(self.request, for_send.my_file.path,
                            attachment=True, attachment_filename=for_send.name)

        return super(FilesView, self).render_to_response(context)
