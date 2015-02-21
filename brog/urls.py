# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin

# TEMP для просомтра загруженных файлов
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView

admin.autodiscover()

from brog.views import *
from filesharing.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'brog.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', index),
    url(r'^accounts/profile/$', TemplateView.as_view(template_name='profile.html')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<full_path>[получаем полный путь])', FilesView.as_view()),

)

# TEMP для просмотра загруженных файлов
urlpatterns +=  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
