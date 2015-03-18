# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from api.serializers import *
from api.permissions import UserPermission
from rest_framework.decorators import detail_route


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
        # return Directory.objects.filter(owner=self.request.user).order_by('full_path')
        return Directory.objects.all().order_by('full_path')

    def perform_create(self, serializer):
        serializer.check_permissions(self.request.user)
        serializer.save(owner=self.request.user)

    @detail_route(methods=['get'])
    def list_dirs(self, request, **kwargs):
        parent = get_object_or_404(Directory, **kwargs)
        self.check_object_permissions(request, parent)
        queryset = Directory.objects.filter(parent=parent)
        return Response(DirectoryRetrieveSerializer(queryset, many=True).data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'])
    def list_files(self, request, **kwargs):
        parent = get_object_or_404(Directory, **kwargs)
        self.check_object_permissions(request, parent)
        queryset = File.objects.filter(parent=parent)
        return Response(FileRetrieveSerializer(queryset, many=True).data,
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
        # return File.objects.filter(owner=self.request.user).order_by('full_path')
        return File.objects.all().order_by('full_path')

    def create(self, request, *args, **kwargs):
        """ Измненён только возвращаемый сериалайзер
        """
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer = FileRetrieveSerializer(serializer.instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.check_permissions(self.request.user)
        serializer.save()