from rest_framework import serializers
from filesharing.models import Directory, File


class ModelCleanMixin(object):
    def validate(self, attrs):
        instance = self.Meta.model(**attrs)
        instance.clean()
        return attrs


class DirectorySerializer(ModelCleanMixin, serializers.ModelSerializer):
    class Meta(object):
        model = Directory
        fields = ('id', 'name', 'parent', 'owner', 'full_path')


class FileSerializer(ModelCleanMixin, serializers.ModelSerializer):
    class Meta(object):
        model = File
        fields = ('id', 'name', 'parent', 'my_file', 'full_path')