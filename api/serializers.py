from rest_framework import serializers, exceptions
from filesharing.models import Directory, File


class ModelCleanMixin(object):
    def validate(self, data):
        instance = self.Meta.model(**data)
        instance.clean()
        return data


class CheckParentPermissionsMixin(object):
    def check_permissions(self, user):
        if not self.validated_data['parent'].has_access(user):
            raise exceptions.PermissionDenied()


class DirectoryCreateSerializer(ModelCleanMixin,
                                CheckParentPermissionsMixin,
                                serializers.ModelSerializer):
    class Meta(object):
        model = Directory
        fields = ('name', 'parent')


class DirectoryRenameSerializer(ModelCleanMixin, serializers.ModelSerializer):
    class Meta(object):
        model = Directory
        fields = ('name', )

    def validate(self, data):
        instance = self.instance
        instance.name = data['name']
        instance.clean()
        return data


class DirectoryRetrieveSerializer(ModelCleanMixin, serializers.ModelSerializer):
    class Meta(object):
        model = Directory
        fields = ('id', 'name', 'parent', 'owner', 'full_path')


class FileUploadSerializer(ModelCleanMixin,
                           CheckParentPermissionsMixin,
                           serializers.ModelSerializer):
    class Meta(object):
        model = File
        fields = ('name', 'parent', 'my_file')


class FileRetrieveSerializer(ModelCleanMixin, serializers.ModelSerializer):
    class Meta(object):
        model = File
        fields = ('id', 'name', 'parent', 'full_path')