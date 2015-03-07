# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from api.views import *

urlpatterns = patterns('',
    url(r'^dir/id/(?P<pk>[0-9]+)/$', DirDetail.as_view()),              # получить директрию по id (методы get, put, delete, post)
    url(r'^dir/path=(?P<path>.+)/$', DirDetail.as_view()),              # получить директорию по полному пути (методы get, put, delete, post)

    url(r'^get/dirs/$', DirList.as_view()),                                 # все директории пользователя
    url(r'^get/dirs/id/(?P<pk>[0-9]+)/$', DirsListByParentId.as_view()),    # список директорий по Id родителя
    url(r'^get/dirs/path=(?P<path>.+)$', DirsListByParentPath.as_view()),   # список директорйи по полному пути родителя


    url(r'^file/id/(?P<pk>[0-9]+)/$', FileDetail.as_view()),              # получить файл по id родителя (методы get, put, delete, post)
    url(r'^file/path=(?P<path>.+)/$', FileDetail.as_view()),              # получить файл по полному пути родителя (методы get, put, delete, post)

    url(r'^file/upload/id/(?P<pk>[0-9]+)/$', FileUpload.as_view()),              # загрузить файл в директорию с указанным id
    url(r'^file/upload/path=(?P<path>.+)/$', FileUpload.as_view()),              # загрузить файл в директорию с указанным полным путем

    url(r'^file/download/id/(?P<pk>[0-9]+)/$', FileDownload.as_view()),              # скачать файл по id
    url(r'^file/download/path=(?P<path>.+)/$', FileDownload.as_view()),              # скачать файл по полному пути

    url(r'^get/files/id/(?P<pk>[0-9]+)/$', FilesListByParentId.as_view()),    # список файлов по Id родителя
    url(r'^get/files/path=(?P<path>.+)/$', FilesListByParentPath.as_view()),   # список файлов по полному пути родителя
)

