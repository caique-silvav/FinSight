from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('finances/', include('finances.urls')),
    path('', include('finances.urls')),
]

# >>> Só para desenvolvimento <<<
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Se você tiver STATICFILES_DIRS, o Django já encontra os arquivos automaticamente