from rest_framework import serializers, exceptions
from filesharing.models import Directory, File


class ValidateCreationMixin(object):
    def validate(self, data):
        if not data['parent'].has_access(self.context['request'].user):
            raise exceptions.PermissionDenied()
        instance = self.Meta.model(**data)
        instance.clean()
        return data


class DirectoryCreateSerializer(ValidateCreationMixin,
                                serializers.ModelSerializer):
    class Meta(object):
        model = Directory
        fields = ('name', 'parent')


class DirectoryRenameSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Directory
        fields = ('name', )

    def validate(self, data):
        instance = self.instance
        instance.name = data['name']
        instance.clean()
        return data


class DirectoryRetrieveSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Directory
        fields = ('id', 'name', 'parent', 'owner', 'full_path')


class MyFileField(serializers.FileField):
    """ Вместо ссылки на физическое расположение файла возвращается ссылка
    на скачивание
    """
    def to_representation(self, value):
        request = self.context.get('request', None)
        return request.build_absolute_uri("/download{}".format(
            value.instance.full_path))


class FileUploadSerializer(ValidateCreationMixin,
                           serializers.ModelSerializer):
    class Meta(object):
        model = File
        fields = ('name', 'parent', 'my_file')

    my_file = MyFileField()


class FileRetrieveSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = File
        fields = ('id', 'name', 'parent', 'full_path', 'my_file')

    my_file = MyFileField()
