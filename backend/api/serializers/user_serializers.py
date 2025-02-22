from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from foodgram.constants import UserConstants
from users.models import Favorite, Follow, Recipe, ShoppingList
from users.validators import validate_correct_username, validate_not_empty

from .avatar_serializers import CostomImageField
from .recipe_serializers import RecipeBriefInfoSerializer

User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = CostomImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации новых пользователей."""

    first_name = serializers.CharField(
        max_length=UserConstants.MAX_FIRST_NAME_LENGTH,
        validators=[validate_not_empty],
        required=True,
    )
    last_name = serializers.CharField(
        max_length=UserConstants.MAX_LAST_NAME_LENGTH,
        validators=[validate_not_empty],
        required=True,
    )
    username = serializers.CharField(
        max_length=UserConstants.MAX_USERNAME_LENGTH,
        validators=[validate_correct_username],
        required=True,
    )

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'first_name',
            'id',
            'last_name',
            'password',
            'username',
        )
        extra_kwargs = {'password': {'write_only': True}}


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    class Meta:
        model = Follow
        fields = ('author', 'user')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о подписке."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'avatar',
            'email',
            'first_name',
            'id',
            'is_subscribed',
            'last_name',
            'recipes_count',
            'recipes',
            'username',
        )
        read_only_fields = (
            'email',
            'first_name',
            'id',
            'last_name',
            'username',
        )

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        return Follow.objects.filter(author=obj, user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = int(request.GET.get('recipes_limit', 6))
        return RecipeBriefInfoSerializer(
            Recipe.objects.filter(author=obj)[:limit],
            many=True,
            context={'request': request},
        ).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('recipe', 'user')
        extra_kwargs = {
            'recipe': {'write_only': True},
            'user': {'write_only': True}
        }

    def to_representation(self, instance):
        return RecipeBriefInfoSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingList
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        """Возвращает краткое представление рецепта."""
        return RecipeBriefInfoSerializer(
            instance.recipe, context={'request': self.context.get('request')}
        ).data
