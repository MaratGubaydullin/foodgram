from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from users.models import (Favorite, Ingredient, Recipe, RecipeToIngredient,
                          ShoppingList, Tag, User)

from .filters import IngredientFilter, RecipeFilter
from .mixins import RecipeActionMixin, SubscriptionMixin
from .pagination import CustomLimitPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (AvatarSerializer, FavoriteRecipeSerializer,
                          IngredientInfoSerializer, RecipeCreateSerializer,
                          RecipeInfoSerializer, ShoppingCartRecipeSerializer,
                          SubscriptionSerializer, TagInfoSerializer,
                          UserProfileSerializer)
from .utils import generate_shopping_list


@require_GET
def short_url_generate(request, pk):
    """Перенаправление по короткой ссылке рецепта."""
    get_object_or_404(Recipe, pk=pk)
    url = reverse("recipes-detail", args=[pk])
    return redirect(url)


class CustomUserViewSet(UserViewSet, SubscriptionMixin):
    """Вьюсет для управления пользователями и подписками."""

    pagination_class = CustomLimitPagination
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    @action(
        methods=['PUT', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated, IsAdminOrAuthorOrReadOnly],
        url_path='me/avatar',
    )
    def avatar_put_delete(self, request, *args, **kwargs):
        """Управление аватаром текущего пользователя."""
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                instance=request.user,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        """Получение профиля текущего пользователя."""
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Обработка подписки/отписки через миксин."""
        return self.handle_subscription(request, id)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions',
    )
    def get_subscriptions(self, request):
        """Получение списка подписок с пагинацией."""
        user = request.user
        queryset = User.objects.filter(follower__user=user).annotate(
            recipes_count=Count('recipes')
        )

        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


class TagListViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagInfoSerializer


class IngredientListViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    permission_classes = [AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientInfoSerializer


class RecipeManagementViewSet(viewsets.ModelViewSet, RecipeActionMixin):
    """Вьюсет для управления рецептами."""

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomLimitPagination
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    queryset = Recipe.objects.select_related(
        'author').prefetch_related('ingredients', 'tags')

    def get_permissions(self):
        """Разрешаем доступ без аутентификации: list, retrieve и get-link."""
        if self.action in ('list', 'retrieve', 'get-link'):
            return [AllowAny()]
        return [IsAdminOrAuthorOrReadOnly()]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action in ('list', 'retrieve', 'get-link'):
            return RecipeInfoSerializer
        return RecipeCreateSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Генерация списка покупок с использованием утилиты."""
        ingredients = RecipeToIngredient.objects.filter(
            recipe__shopping_list__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            sum=Sum('amount'),
        )

        return HttpResponse(
            generate_shopping_list(ingredients),
            content_type='text/plain',
            headers={
                'Content-Disposition': (
                    'attachment; filename="shopping_list.txt"'
                ),
            },
        )

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[AllowAny],
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return Response({
            'short-link': request.build_absolute_uri(
                reverse('short_url', args=[recipe.pk])
            )
        },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='favorite',
    )
    def add_to_favorite(self, request, pk):
        """Добавление/удаление из избранного через миксин."""
        self.initialize_action(
            model_class=Favorite,
            serializer_class=FavoriteRecipeSerializer,
            exists_message='Рецепт "{}" уже в избранном',
            not_exists_message='Рецепта нет в избранном'
        )
        return self.handle_recipe_action(request, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
    )
    def add_to_shopping_cart(self, request, pk):
        """Добавление/удаление из списка покупок через миксин."""
        self.initialize_action(
            model_class=ShoppingList,
            serializer_class=ShoppingCartRecipeSerializer,
            exists_message='Рецепт "{}" уже в списке покупок',
            not_exists_message='Рецепта нет в списке покупок'
        )
        return self.handle_recipe_action(request, pk)
