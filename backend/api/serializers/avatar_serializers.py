import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class CostomImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if data is None:
            return None

        if not isinstance(data, str):
            raise serializers.ValidationError(
                "Ожидается строка, содержащая base64 данные изображения")

        try:
            if data.startswith('data:image'):
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr),
                                   name='temp.' + ext)
            return super().to_internal_value(data)
        except (ValueError, TypeError, OSError, base64.binascii.Error) as e:
            raise serializers.ValidationError(
                f"Некорректные base64 данные изображения: {e}")
