from . import views
from django.urls import path
from .utils import  chat_view_teste

urlpatterns = [
    path('', views.index, name='index'),
    path('chat_view/', views.chat_view, name='chat_view'),
    path('get_termos_juridicos/', views.get_termos_juridicos, name='get_termos_juridicos'),
    path('chat_view_teste/', chat_view_teste, name='chat_view_teste'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
