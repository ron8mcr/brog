# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages

from filesharing.models import Directory, File
from filesharing.forms import CreateDirectoryForm, UploadFileForm, UpdateDirectoryNameForm

from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView

# переопределячем значение тэга сообщения под стиль бутстрапа,
# чтобы вместо error стал danger
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {message_constants.ERROR: 'danger', }


class IndexView(TemplateView):
    template_name = 'index.html'


class DirFileCreate(CreateView):

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        # заполняем неполученные поля
        self.parent_path = self.kwargs['path']
        form.instance.parent = Directory.objects.get_by_full_path(
            self.parent_path)
        form.instance.owner = self.request.user

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.success_url = self.parent_path
        form.instance.save()
        return super(DirFileCreate, self).form_valid(form)

    def form_invalid(self, form):
        # TODO: ошибки полей
        for err_type in form.errors:
            for err in form.errors[err_type]:
                messages.add_message(self.request, messages.ERROR, err)
        return HttpResponseRedirect(self.parent_path)


class DirUpdate(UpdateView):

    def get_object(self, queryset=None):
        return Directory.objects.get_by_full_path(self.kwargs['path'])

    def form_valid(self, form):
        for_rename = self.get_object()
        instance = form.save(commit=False)

        # домашние папки изменять нельзя
        if for_rename in Directory.objects.root_nodes():
            messages.add_message(self.request, messages.ERROR,
                            "Невозможно переименовать домашнюю директорию")
            return HttpResponseRedirect(self.kwargs['path'])

        instance.save()
        messages.add_message(self.request, messages.SUCCESS,
                    "Директория \"{}\" успешно переименована в \"{}\"".format(
                    for_rename.name, instance.name))
        return HttpResponseRedirect(instance.full_path)

    def form_invalid(self, form):
        for err_type in form.errors:
            for err in form.errors[err_type]:
                messages.add_message(self.request, messages.ERROR, err)
        return HttpResponseRedirect(self.parent_path)


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

    def navigation_inform(self):
        """
        :return:информация для полей навигации
        """
        result = dict()

        # папки, составляющие полный пусть (для СТРОКИ навигации)
        result['path_dirs'] = self.cur_dir.get_ancestors(
            include_self=True)

        # дерево папок пользователя - для ДЕРЕВА навигации
        result['user_dirs'] = self.request.user.home_directory.get_descendants(
            include_self=True)
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
            context['UpdateDirectoryNameForm'] = self.get_form(
                UpdateDirectoryNameForm)
        return context

    def prepare_file_context(self, context):
        self.cur_dir = self.cur_file.parent
        if not self.cur_file.has_access(self.request.user):
            context['critical_error'] = self.errors['ACCESS_DENIED']
        else:
            context['file'] = self.cur_file
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
            # если по запрошенному пути найден файл
            self.cur_file = File.objects.get_by_full_path(path)
            if self.cur_file:
                context = self.prepare_file_context(context)
            else:
                context['critical_error'] = self.errors['BAD_PATH']

        return context

    def render_to_response(self, context):
        if 'file' in context:
            response = HttpResponse()
            response['Content-Disposition'] = "attachment; filename=" + \
                context['file'].name
            response['X-Accel-Redirect'] = context['file'].my_file.url
            return response

        return super(FilesView, self).render_to_response(context)
