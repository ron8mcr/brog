# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from filesharing.views import FileUpload, DirCreate, DirUpdate, DirDelete, \
    FilesView, FileDelete, download_file


urlpatterns = patterns('',
    url(r'^upload/file/path=(?P<full_path>.+)$',
        FileUpload.as_view()),
    url(r'^create/dir/path=(?P<full_path>.+)$',
        DirCreate.as_view()),
    url(r'^update/dir/path=(?P<full_path>.+)$',
        DirUpdate.as_view()),
    url(r'^delete/dir/path=(?P<full_path>.+)$',
        DirDelete.as_view()),
    url(r'^download(?P<full_path>.+)$', download_file, name="download"),
    url(r'^delete/file/path=(?P<full_path>.+)$',
        FileDelete.as_view()),
    url(r'(?P<full_path>.+)/$', FilesView.as_view()),
)