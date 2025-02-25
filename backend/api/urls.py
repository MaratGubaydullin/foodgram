from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientListViewSet,
                    RecipeManagementViewSet, TagListViewSet)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('ingredients', IngredientListViewSet,
                   basename='ingredients')
router_v1.register('recipes', RecipeManagementViewSet,
                   basename='recipes')
router_v1.register('tags', TagListViewSet,
                   basename='tags')
router_v1.register('users', CustomUserViewSet,
                   basename='users')

urls = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('docs/', TemplateView.as_view(template_name='docs/redoc.html'),
         name='redoc'),
    path('', include(router_v1.urls))
]
