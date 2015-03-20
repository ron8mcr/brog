# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from api.serializers import *
from api.permissions import UserPermission


class AuthPermClassesMixin(object):
    authentication_classes = (SessionAuthentication,
                              BasicAuthentication, TokenAuthentication)
    permission_classes = [UserPermission]


class DirectoryViewSet(AuthPermClassesMixin,
                       viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DirectoryCreateSerializer
        elif self.request.method == 'PUT':
            return DirectoryRenameSerializer
        else:
            return DirectoryRetrieveSerializer

    def get_object(self):
        obj = get_object_or_404(Directory, **self.kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        return Directory.objects.filter(
            owner=self.request.user).order_by('full_path')
        # return Directory.objects.all().order_by('full_path')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @detail_route(methods=['get'])
    def list_dirs(self, request, **kwargs):
        return self.list_content(request, Directory,
                                 DirectoryRetrieveSerializer, **kwargs)

    @detail_route(methods=['get'])
    def list_files(self, request, **kwargs):
        return self.list_content(request, File,
                                 FileRetrieveSerializer, **kwargs)

    def list_content(self, request, klass, serializer, **kwargs):
        parent = get_object_or_404(Directory, **kwargs)
        self.check_object_permissions(request, parent)
        queryset = klass.objects.filter(parent=parent)
        serializer.context = {'request': request}
        return Response(serializer(queryset, many=True,
                                   context=self.get_serializer_context()).data,
                        status=status.HTTP_200_OK)


class FileViewSet(AuthPermClassesMixin,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FileUploadSerializer
        else:
            return FileRetrieveSerializer

    def get_object(self):
        obj = get_object_or_404(File, **self.kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        return File.objects.filter(
            owner=self.request.user).order_by('full_path')
        # return File.objects.all().order_by('full_path')
