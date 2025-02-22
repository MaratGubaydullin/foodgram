from api.urls import urls as api_urls
from api.views import short_url_generate
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
    path('s/<int:pk>/', short_url_generate, name='short_url')
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL,
#                           document_root=settings.STATIC_ROOT)
