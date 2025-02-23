from django.contrib.auth.models import AbstractUser
from django.db import models

from django.conf import settings

from .validators import (amount_range_validator, validate_correct_username,
                         validate_not_empty, validate_username)


class Follow(models.Model):
    """Модель, представляющая подписку пользователя на автора."""

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_following_author'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='check_user_not_following_self'
            ),
        ]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'


class User(AbstractUser):
    """Расширенная модель пользователя."""

    username = models.CharField(
        'Имя пользователя',
        validators=[validate_correct_username, validate_username],
        max_length=settings.MAX_USERNAME_LENGTH,
        unique=True,
        null=False,
        db_index=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.MAX_FIRST_NAME_LENGTH,
        blank=True,
        validators=[validate_not_empty]
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.MAX_LAST_NAME_LENGTH,
        blank=True,
        validators=[validate_not_empty]
    )
    email = models.EmailField(
        'email',
        max_length=settings.MAX_EMAIL_LENGTH,
        unique=True
    )
    avatar = models.ImageField(
        'Фото профиля',
        blank=True,
        null=True,
        upload_to='media/users_avatars/'
    )

    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'password',
        'username'
    ]
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Имя пользователя'
        verbose_name_plural = 'Имена пользователей'
        ordering = ('username',)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Favorite(models.Model):
    """Модель для хранения избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe_for_user'),
        )

    def __str__(self):
        return (f'Рецепт: {self.recipe} добавлен в избранное '
                f'пользователю {self.user}')


class Recipe(models.Model):
    """Модель, представляющая рецепт."""

    name = models.CharField(
        'Название',
        max_length=settings.MAX_RECIPE_NAME_LENGTH,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeToIngredient',
        verbose_name='Список ингредиентов'
    )
    text = models.CharField(
        'Как готовить блюдо',
        max_length=settings.MAX_RECIPE_TEXT_LENGTH,
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[amount_range_validator],
        verbose_name='Время приготовления (в минутах)'
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги'
    )
    image = models.ImageField(
        verbose_name='Картинка блюда',
        upload_to='media/recipes_images/'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class ShoppingList(models.Model):
    """Модель, представляющая список покупок пользователя."""

    user = models.ForeignKey(
        User,
        related_name='shopping_list',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_list',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe_user_shopplist'
            ),
        )

    def __str__(self):
        return (f'Рецепт {self.recipe} в списке покупок у: {self.user}')


class Ingredient(models.Model):
    """Модель, представляющая ингредиент."""

    name = models.CharField(
        'Название',
        max_length=settings.MAX_INGREDIENT_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.MAX_MEASUREMENT_UNIT_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeToIngredient(models.Model):
    """Модель, связывающая рецепт и ингредиент с указанием количества."""

    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredient_list',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient',
        verbose_name='ингредиент',
        on_delete=models.RESTRICT
    )
    amount = models.PositiveSmallIntegerField(
        validators=[amount_range_validator],
        verbose_name='Количество',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredients_in_recipe',
            ),
        )

    def __str__(self):
        return (f'Рецепт {self.recipe} уже содержит ингредиент '
                f'ингредиент {self.ingredient}')


class Tag(models.Model):
    """Модель, представляющая тег."""

    name = models.CharField(
        "Название",
        unique=True,
        max_length=settings.TAG_MAX_LENGTH,
    )
    slug = models.CharField(
        'Slug',
        unique=True,
        max_length=settings.TAG_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
