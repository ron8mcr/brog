# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from filesharing.models import Directory, File
from api.serializers import DirectorySerializer, FileSerializer
from sendfile import sendfile


class AuthPermClassesMixin(object):
    authentication_classes = (SessionAuthentication,
                              BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)


class DirDetail(AuthPermClassesMixin, generics.GenericAPIView):
    serializer_class = DirectorySerializer

    def get(self, request, **kwargs):
        cur_dir = get_object_or_404(Directory, **kwargs)
        if cur_dir.has_access(self.request.user):
            serializer = DirectorySerializer(cur_dir)
            return Response(serializer.data)
        else:
            raise exceptions.PermissionDenied()

    def post(self, request, **kwargs):
        parent_dir = get_object_or_404(Directory, **kwargs)
        self.request.data['owner'] = self.request.user.id
        self.request.data['parent'] = parent_dir.id
        serializer = DirectorySerializer(data=self.request.data)
        if parent_dir.has_access(self.request.user):
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.PermissionDenied()

    def put(self, request, **kwargs):
        cur_dir = get_object_or_404(Directory, **kwargs)
        serializer = DirectorySerializer(cur_dir, data=request.data)

        if cur_dir.has_access(self.request.user) and \
                        cur_dir not in Directory.objects.root_nodes():
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.PermissionDenied()

    def delete(self, request, **kwargs):
        cur_dir = get_object_or_404(Directory, **kwargs)

        if cur_dir.has_access(self.request.user) and \
                        cur_dir not in Directory.objects.root_nodes():
            cur_dir.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.PermissionDenied()


class FileDetail(AuthPermClassesMixin, generics.GenericAPIView):
    serializer_class = FileSerializer

    def get(self, request, **kwargs):
        file = get_object_or_404(File, **kwargs)
        if file.has_access(self.request.user):
            serializer = FileSerializer(file)
            return Response(serializer.data)
        else:
            raise exceptions.PermissionDenied()

    def delete(self, request, **kwargs):
        file = get_object_or_404(klass=File, **kwargs)
        if file.has_access(self.request.user):
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.PermissionDenied()

    def post(self, request, **kwargs):
        cur_dir = get_object_or_404(Directory, **kwargs)
        self.request.data['parent'] = cur_dir.id
        serializer = FileSerializer(data=self.request.data)
        if cur_dir.has_access(self.request.user):
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.PermissionDenied()


class DirsList(AuthPermClassesMixin, generics.ListAPIView):
    serializer_class = DirectorySerializer

    def get_queryset(self):
        cur_dir = get_object_or_404(Directory, **self.kwargs)
        if cur_dir.has_access(self.request.user):
            return get_list_or_404(Directory, parent=cur_dir)
        else:
            raise exceptions.PermissionDenied()


class FilesList(AuthPermClassesMixin, generics.ListAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        cur_dir = get_object_or_404(Directory, **self.kwargs)
        if cur_dir.has_access(self.request.user):
            return get_list_or_404(File, parent=cur_dir)
        else:
            raise exceptions.PermissionDenied()


class FileDownload(AuthPermClassesMixin, APIView):

    def get(self, request, **kwargs):
        file = get_object_or_404(File, **kwargs)
        if file.has_access(self.request.user):
            sendfile(self.request, file.my_file.path,
                     attachment=True, attachment_filename=file.name)
        else:
            raise exceptions.PermissionDenied()
