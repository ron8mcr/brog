# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.conf.urls.static import static

# TEMP для просомтра загруженных файлов
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', TemplateView.as_view(
        template_name='profile.html')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(r'^', include('filesharing.urls', namespace='filesharing')),
)

# TEMP для просмотра загруженных файлов
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
