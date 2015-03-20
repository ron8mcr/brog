# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from api.views import DirectoryViewSet, FileViewSet

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
     url(r'^dir/path/(?P<full_path>.+)/list_dirs/$',
         DirectoryViewSet.as_view({'get': 'list_dirs'})),
     url(r'^dir/path/(?P<full_path>.+)/list_files/$',
         DirectoryViewSet.as_view({'get': 'list_files'})),
     url(r'^dir/path/(?P<full_path>.+)$', dir_detail),
     url(r'^file/path/(?P<full_path>.+)$', file_detail),
     url(r'^', include(router.urls)),
)
