from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Agregar esta línea

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web_skill_app.urls')),
]

# Solo para desarrollo (comentado temporalmente)
# if settings.DEBUG:
#     urlpatterns += [
#         path("__reload__/", include("django_browser_reload.urls")),
#     ]