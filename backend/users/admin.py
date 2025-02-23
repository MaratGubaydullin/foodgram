from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (Favorite, Ingredient, Recipe, RecipeToIngredient,
                     ShoppingList, Tag, User)

EMPTY_FIELD_VALUE = 'Не задано'
INLINE_FORM_EXTRA = 1


class AuthorFilter(AutocompleteFilter):
    title = 'Автор рецепта'
    field_name = 'author'


class IngredientFilter(AutocompleteFilter):
    title = 'Ингредиент'
    field_name = 'ingredients'


class RecipeFilter(AutocompleteFilter):
    title = 'Рецепт'
    field_name = 'recipe'


class TagFilter(AutocompleteFilter):
    title = 'Тег'
    field_name = 'tags'


class UserFilter(AutocompleteFilter):
    title = 'Пользователь'
    field_name = 'user'


class RecipeToIngredientInLine(admin.TabularInline):
    model = RecipeToIngredient
    extra = INLINE_FORM_EXTRA
    autocomplete_fields = ('ingredient',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'recipe', 'ingredient'
        )


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Admin configuration for the custom user model."""

    empty_value_display = EMPTY_FIELD_VALUE
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'date_joined',
        'last_login',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Personal Info',
            {'fields': ('first_name', 'last_name', 'avatar')},
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    empty_value_display = EMPTY_FIELD_VALUE
    list_display = ('user', 'recipe')
    list_filter = (UserFilter, RecipeFilter)
    autocomplete_fields = ('user', 'recipe')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'recipe'
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = EMPTY_FIELD_VALUE
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = EMPTY_FIELD_VALUE
    filter_horizontal = ('tags',)
    inlines = (RecipeToIngredientInLine,)
    list_display = ('name', 'author', 'get_favorite_count')
    list_filter = (AuthorFilter, IngredientFilter, TagFilter)
    search_fields = ('name',)
    autocomplete_fields = ('author',)

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favorite.count()

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('author')
            .prefetch_related('ingredients', 'tags', 'favorite')
        )


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    empty_value_display = EMPTY_FIELD_VALUE
    list_display = ('user', 'recipe')
    list_filter = (UserFilter, RecipeFilter)
    autocomplete_fields = ('user', 'recipe')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'recipe'
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    empty_value_display = EMPTY_FIELD_VALUE
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}
