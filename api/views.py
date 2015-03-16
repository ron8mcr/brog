# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from filesharing.models import Directory, File
from api.serializers import DirectorySerializer, FileSerializer

from api.permissions import UserPermission


class AuthPermClassesMixin(object):
    authentication_classes = (SessionAuthentication,
                              BasicAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, UserPermission)


class DirDetail(AuthPermClassesMixin, generics.GenericAPIView):
    serializer_class = DirectorySerializer

    def get(self, request, **kwargs):
        cur_dir = get_object_or_404(Directory, **kwargs)
        serializer = DirectorySerializer(cur_dir)
        return Response(serializer.data)

    def post(self, request, **kwargs):
        parent_dir = get_object_or_404(Directory, **kwargs)
        self.request.DATA['owner'] = self.request.user.id
        self.request.DATA['parent'] = parent_dir.id
        serializer = DirectorySerializer(data=self.request.DATA)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        cur_dir = get_object_or_404(Directory, **kwargs)
        serializer = DirectorySerializer(cur_dir, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        cur_dir = get_object_or_404(Directory, **kwargs)
        cur_dir.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FileDetail(AuthPermClassesMixin, generics.GenericAPIView):
    serializer_class = FileSerializer

    def get(self, request, **kwargs):
        file = get_object_or_404(File, **kwargs)
        serializer = FileSerializer(file)
        return Response(serializer.data)

    def delete(self, request, **kwargs):
        file = get_object_or_404(klass=File, **kwargs)
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, **kwargs):
        cur_dir = get_object_or_404(Directory, **kwargs)
        data = self.request.POST.copy()
        data.update(self.request.FILES.copy())
        data['parent'] = cur_dir.id
        serializer = FileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DirsList(AuthPermClassesMixin, generics.ListAPIView):
    serializer_class = DirectorySerializer

    def get_queryset(self):
        cur_dir = get_object_or_404(Directory, **self.kwargs)
        return get_list_or_404(Directory, parent=cur_dir)


class FilesList(AuthPermClassesMixin, generics.ListAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        cur_dir = get_object_or_404(Directory, **self.kwargs)
        get_list_or_404(File, parent=cur_dir)