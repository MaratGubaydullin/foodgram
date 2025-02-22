from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from users.models import Follow, Recipe, User
from api.serializers import SubscriptionSerializer


class RecipeActionMixin:
    """
    Миксин для обработки действий с рецептами
    Реализует общую логику для добавления/удаления в избранное и список покупок
    """

    def initialize_action(self, model_class,
                          serializer_class, exists_message,
                          not_exists_message):
        self.model_class = model_class
        self.serializer_class = serializer_class
        self.exists_message = exists_message
        self.not_exists_message = not_exists_message

    def handle_recipe_action(self, request, pk):
        """Основной метод обработки POST/DELETE запросов"""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        exists = self.model_class.objects.filter(recipe=recipe,
                                                 user=user).exists()

        if request.method == 'POST':
            return self._handle_post(recipe, user, exists)
        return self._handle_delete(recipe, user, exists)

    def _handle_post(self, recipe, user, exists):
        """Обработка POST запроса"""
        if exists:
            return Response(
                {'detail': self.exists_message.format(recipe.name)},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(
            data={'recipe': recipe.id, 'user': user.id},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _handle_delete(self, recipe, user, exists):
        """Обработка DELETE запроса"""
        if not exists:
            return Response(
                {'detail': self.not_exists_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.model_class.objects.filter(recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionMixin:
    """
    Миксин для обработки подписок
    Реализует логику подписки/отписки на пользователей
    """

    def handle_subscription(self, request, id):
        """Основной метод обработки подписок."""
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                {'errors': 'Нельзя выполнить действие для себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            return self._create_subscription(user, author)

        return self._delete_subscription(user, author)

    def _create_subscription(self, user, author):
        """Создание подписки"""
        if Follow.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Подписка уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Follow.objects.create(user=user, author=author)
        return self._get_subscription_response(author)

    def _delete_subscription(self, user, author):
        """Удаление подписки"""
        deleted_count, _ = Follow.objects.filter(
            user=user, author=author).delete()
        if not deleted_count:
            return Response(
                {'detail': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_subscription_response(self, author):
        """Формирование ответа с данными подписки"""
        author_data = User.objects.annotate(
            recipes_count=Count('recipes')).get(id=author.id)
        serializer = SubscriptionSerializer(
            author_data, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
