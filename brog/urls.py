# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin

# TEMP для просомтра загруженных файлов
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

from filesharing.views import *

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', TemplateView.as_view(
        template_name='profile.html')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/file/path=(?P<path>.+)$',
        DirFileCreate.as_view(form_class=UploadFileForm)),
    url(r'^create/dir/path=(?P<path>.+)$',
        DirFileCreate.as_view(form_class=CreateDirectoryForm)),
    url(r'^update/dir/path=(?P<path>.+)$',
        DirUpdate.as_view(form_class=UpdateDirectoryNameForm)),
    url(r'^delete/dir/path=(?P<path>.+)$',
        DirDelete.as_view()),
    url(r'(?P<path>.+)/$', FilesView.as_view()),

)

# TEMP для просмотра загруженных файлов
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
