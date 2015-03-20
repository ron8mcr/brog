# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin, CreateView, UpdateView, \
    DeleteView
from sendfile import sendfile
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from filesharing.models import Directory, File
from filesharing.forms import CreateDirectoryForm, UploadFileForm, \
    UpdateDirectoryNameForm


class SetupFormInstanceAndChecksMixin(object):
    """ Миксин для добавления дополнительных полей в экземпляр
    И дополнительных проверок, например, на права доступа
    """

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        try:
            # если появились какие-либо ошибки при добавлении полей в форму,
            # метод сам должен записать эти ошибки и бросить исключение
            form = self.setup_form_instance(form)
        except ValidationError as err:
            return self.form_invalid(form)

        self.additional_checks(form)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def setup_form_instance(self, form):
        return form

    def additional_checks(self, form):
        pass


class FormErrorMessagesMixin(object):
    def form_invalid(self, form):
        for err_type in form.errors:
            for err in form.errors[err_type]:
                messages.add_message(self.request, messages.ERROR, err)
        return HttpResponseRedirect(self.kwargs['full_path'])


class DirCreate(SetupFormInstanceAndChecksMixin,
                FormErrorMessagesMixin, CreateView):
    template_name = 'home.html'
    form_class = CreateDirectoryForm

    def setup_form_instance(self, form):
        form.instance.owner = self.request.user
        try:
            form.instance.parent = Directory.objects.get(
                full_path=self.kwargs['full_path'])
        except Directory.DoesNotExist:
            form.add_error(None, "Неверный путь")
            raise ValidationError
        return form

    def additional_checks(self, form):
        if not form.instance.parent.has_access(self.request.user):
            form.add_error(None,
                           "Вы не имеете прав доступа к данной директории!")

    def form_valid(self, form):
        self.success_url = self.kwargs['full_path']
        messages.add_message(self.request, messages.SUCCESS,
                             "Директория \"{}\" успешно cоздана".format(
                                 form.instance.name))
        return super(DirCreate, self).form_valid(form)


class FileUpload(SetupFormInstanceAndChecksMixin,
                 FormErrorMessagesMixin, CreateView):
    template_name = 'home.html'
    form_class = UploadFileForm

    def setup_form_instance(self, form):
        try:
            form.instance.parent = Directory.objects.get(
                full_path=self.kwargs['full_path'])
        except Directory.DoesNotExist:
            form.add_error(None, "Неверный путь")
            raise ValidationError
        return form

    def additional_checks(self, form):
        if not form.instance.parent.has_access(self.request.user):
            form.add_error(None,
                           "Вы не имеете прав доступа к данной директории!")

    def form_valid(self, form):
        self.success_url = self.kwargs['full_path']
        messages.add_message(self.request, messages.SUCCESS,
                             "Файл \"{}\" успешно загружен".format(
                                 form.instance.name))
        return super(FileUpload, self).form_valid(form)


class DirUpdate(SetupFormInstanceAndChecksMixin,
                FormErrorMessagesMixin, UpdateView):
    form_class = UpdateDirectoryNameForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(DirUpdate, self).post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return Directory.objects.get(full_path=self.kwargs['full_path'])

    def additional_checks(self, form):
        for_rename = self.get_object()
        if for_rename in Directory.objects.root_nodes():
            form.add_error(None, "Невозможно переименовать домашнюю директорию")
            return
        if not for_rename.has_access(self.request.user):
            form.add_error(
                None, "Вы не имеете прав доступа к данной директории!")

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
        return get_object_or_404(Directory, full_path=self.kwargs['full_path'])

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


class FileDelete(DeleteView):
    model = File

    def get_object(self, queryset=None):
        return get_object_or_404(File, full_path=self.kwargs['full_path'])

    def delete(self, request, *args, **kwargs):
        file_for_del = self.get_object()
        parent_path = file_for_del.parent.full_path

        if file_for_del.has_access(self.request.user):
            file_for_del.delete()
            messages.add_message(self.request, messages.SUCCESS,
                                 "Файл был успешно удален")
        else:
            messages.add_message(self.request, messages.ERROR,
                                 "Вы не имеете право удалять данный файл")
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

    def get_context_data(self, **context):
        path = self.kwargs['full_path']
        context['messages'] = messages.get_messages(self.request)

        try:
            context.update(self.prepare_dir_context(
                Directory.objects.get(full_path=path)))
        except Directory.DoesNotExist:
            try:
                context.update(self.prepare_file_context(
                    File.objects.get(full_path=path)))
            except (Directory.DoesNotExist, File.DoesNotExist):
                context['critical_error'] = self.errors['BAD_PATH']

        return super(FilesView, self).get_context_data(**context)


def download_file(request, **kwargs):
    file_ = get_object_or_404(File, full_path=kwargs['full_path'])
    if file_.has_access(request.user):
        return sendfile(request, file_.my_file.path,
                        attachment=True, attachment_filename=file_.name)
    else:
        raise PermissionDenied()
