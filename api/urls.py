# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from api.views import *

# urlpatterns = patterns('',
#     # получить директрию по id/path
#     url(r'^dir/id/(?P<pk>[0-9]+)/$', DirDetail.as_view()),
#     url(r'^dir/path=(?P<full_path>.+)/$', DirDetail.as_view()),
#
#     # список директорий по Id/path родителя
#     url(r'^get/dirs/id/(?P<pk>[0-9]+)/$', DirsList.as_view()),
#     url(r'^get/dirs/path=(?P<full_path>.+)$', DirsList.as_view()),
#
#     # список файлов по id/path родителя
#     url(r'^get/files/id/(?P<pk>[0-9]+)/$', FilesList.as_view()),
#     url(r'^get/files/path=(?P<full_path>.+)/$', FilesList.as_view()),
#
#     # файл по id/path
#     url(r'^file/id/(?P<pk>[0-9]+)/$', FileDetail.as_view()),
#     url(r'^file/path=(?P<full_path>.+)/$', FileDetail.as_view()),
# )

router = DefaultRouter()
router.register(r'dir', DirectoryViewSet, base_name='Directory')
router.register(r'file', FileViewSet, base_name='File')

dir_detail = DirectoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

file_detail = FileViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

urlpatterns = patterns('',
     url(r'^dir/path/(?P<full_path>.+)/list_dirs/$', DirectoryViewSet.as_view({'get': 'list_dirs'})),
     url(r'^dir/path/(?P<full_path>.+)/list_files/$', DirectoryViewSet.as_view({'get': 'list_files'})),
     url(r'^dir/path/(?P<full_path>.+)$', dir_detail),
     url(r'^file/path/(?P<full_path>.+)$', file_detail),
     url(r'^', include(router.urls)),
)

