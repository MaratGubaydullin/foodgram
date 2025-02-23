from djoser.serializers import UserSerializer
from django.db import transaction
from rest_framework import serializers

from users.models import (Favorite, Ingredient, Recipe, RecipeToIngredient,
                          ShoppingList, Tag, User)

from .avatar_serializers import CustomImageField


class UserProfileSerializer(UserSerializer):
    """Сериализатор для представления информации о пользователе."""

    avatar = CustomImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'avatar',
            'email',
            'first_name',
            'id',
            'is_subscribed',
            'last_name',
            'username',
        )
        read_only_fields = ('id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли текущий пользователь на автора."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиента в рецепте."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeToIngredient
        fields = ('id', 'amount')


class RecipeIngredientInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeToIngredient
        fields = (
            'amount',
            'id',
            'measurement_unit',
            'name',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, label='Tags'
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True, label='Ingredients'
    )
    image = CustomImageField(allow_null=True, label='images')

    class Meta:
        model = Recipe
        fields = (
            'cooking_time',
            'image',
            'ingredients',
            'name',
            'tags',
            'text',
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def create_ingredients(self, ingredients, recipe):
        """Создает связи между рецептом и ингредиентами."""
        result = []
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            recipe_ingredient = RecipeToIngredient(
                ingredient_id=ingredient_id,
                recipe=recipe,
                amount=amount
            )
            result.append(recipe_ingredient)
        RecipeToIngredient.objects.bulk_create(result)

    def create_tags(self, tags, recipe):
        """Устанавливает теги для рецепта."""
        recipe.tags.set(tags)

    def to_representation(self, instance):
        """Возвращает полное представление рецепта."""
        serializer = RecipeInfoSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        RecipeToIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)
        self.create_tags(tags, instance)
        return super().update(instance, validated_data)

    def validate(self, data):
        """Валидирует данные рецепта."""
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Добавьте хотя бы один ингредиент !'})
        ingredients_ids = [ingredient['id'] for ingredient in ingredients]
        existing_ingredients = Ingredient.objects.filter(
            id__in=ingredients_ids)
        if existing_ingredients.count() != len(ingredients_ids):
            missing_ids = set(ingredients_ids) - set(
                existing_ingredients.values_list('id', flat=True)
            )
            raise serializers.ValidationError(
                f'Ингредиент с id: {missing_ids} не существует !')
        data['ingredients'] = ingredients

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Добавьте хотя бы один тег !'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не должны повторяться !')
        data['tags'] = tags
        return data


class TagInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о рецепте."""

    author = UserProfileSerializer()
    ingredients = RecipeIngredientInfoSerializer(
        source='ingredient_list', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagInfoSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'author',
            'cooking_time',
            'id',
            'image',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'tags',
            'text',
        )

    def check_user_status(self, obj, model_class):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and model_class.objects.filter(recipe=obj,
                                           user=request.user).exists()
        )

    def get_is_favorited(self, obj):
        """Определяет, находится ли рецепт в списке избранного пользователя."""
        return self.check_user_status(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        """Определяет, находится ли рецепт в списке покупок пользователя."""
        return self.check_user_status(obj, ShoppingList)


class RecipeBriefInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
