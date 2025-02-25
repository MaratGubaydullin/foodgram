import re

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.conf import settings

MIN_LEN_USERNAME = 3
MAX_LEN_USERNAME = 150


def validate_not_empty(value):
    if not value or str(value).strip() == '':
        raise ValidationError(
            _('Это поле не может быть пустым.'),
            code='required'
        )


def validate_correct_username(data):
    if data.lower() == 'me':
        raise ValidationError('Имя пользователя не может быть "me"')
    if not re.match(r'^[\w.@+-]+$', data):
        raise ValidationError(
            'Имя пользователя может содержать только буквы, '
            'цифры и символы @/./+/-/_'
        )
    if len(data) < MIN_LEN_USERNAME or len(data) > MAX_LEN_USERNAME:
        raise ValidationError(
            f'Имя пользователя должно быть от {MIN_LEN_USERNAME} '
            f'до {MAX_LEN_USERNAME} символов.'
        )


def amount_range_validator(value):
    if value < settings.MIN_INGREDIENT_AMOUNT:
        raise ValidationError(
            'Неверное количество ингредиента! Не меньше: '
            f'{settings.MIN_INGREDIENT_AMOUNT} !'
        )
    if value > settings.MAX_INGREDIENT_AMOUNT:
        raise ValidationError(
            'Неверное количество ингредиента! Не больше: '
            f'{settings.MAX_INGREDIENT_AMOUNT} !'
        )


def cooking_time_range_validator(value):
    if value < settings.MIN_COOKING_TIME:
        raise ValidationError(
            'Минимальное время приготовления - '
            f'{settings.MIN_COOKING_TIME} мин. !'
        )
    if value > settings.MAX_COOKING_TIME:
        raise ValidationError(
            'Максимальное время приготовления - '
            f'{settings.MAX_COOKING_TIME} мин. !'
        )


validate_username = UnicodeUsernameValidator()
