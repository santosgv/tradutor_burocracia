
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Core.urls')),
    path('auth/', include('Autenticacao.urls')),
]
