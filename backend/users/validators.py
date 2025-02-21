import re

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from foodgram.constants import IngredientConstants, RecipeConstants

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
    if value < IngredientConstants.MIN_INGREDIENT_AMOUNT:
        raise ValidationError(
            f'Неверное количество ингредиента! Не меньше: '
            f'{IngredientConstants.MIN_INGREDIENT_AMOUNT} !'
        )
    if value > IngredientConstants.MAX_INGREDIENT_AMOUNT:
        raise ValidationError(
            f'Неверное количество ингредиента! Не больше: '
            f'{IngredientConstants.MAX_INGREDIENT_AMOUNT} !'
        )


def cooking_time_range_validator(value):
    if value < RecipeConstants.MIN_COOKING_TIME:
        raise ValidationError(
            f'Минимальное время приготовления - '
            f'{RecipeConstants.MIN_COOKING_TIME} мин. !'
        )
    if value > RecipeConstants.MAX_COOKING_TIME:
        raise ValidationError(
            f'Максимальное время приготовления - '
            f'{RecipeConstants.MAX_COOKING_TIME} мин. !'
        )


validate_username = UnicodeUsernameValidator()
