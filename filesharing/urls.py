# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from filesharing.views import FileUpload, DirCreate, DirUpdate, DirDelete, FilesView


urlpatterns = patterns('',
    url(r'^upload/file/path=(?P<path>.+)$',
        FileUpload.as_view()),
    url(r'^create/dir/path=(?P<path>.+)$',
        DirCreate.as_view()),
    url(r'^update/dir/path=(?P<path>.+)$',
        DirUpdate.as_view()),
    url(r'^delete/dir/path=(?P<path>.+)$',
        DirDelete.as_view()),
    url(r'(?P<path>.+)/$', FilesView.as_view()),
)