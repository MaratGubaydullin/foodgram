import re

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from .constants import IngredientConstants, RecipeConstants


MIN_LEN_USERNAME = 3
MAX_LEN_USERNAME = 150


def validate_correct_username(data):
    if data.lower() == 'me':
        raise ValidationError('Имя пользователя не может быть "me"')
    if not re.match(r'^[\w.@+-]+$', data):
        raise ValidationError('Имя пользователя содержит недопустимый символ')
    if len(data) < MIN_LEN_USERNAME or len(data) > MAX_LEN_USERNAME:
        raise ValidationError(
            'Имя пользователя должно иметь длину от 3 до 150 символов.')


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
