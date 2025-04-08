from . import views
from django.urls import path

urlpatterns = [
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('logar/', views.logar, name='logar'),
    path('sair/', views.sair, name="sair"),
]
