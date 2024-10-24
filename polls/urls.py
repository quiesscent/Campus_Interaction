from django.urls import path
from . import views

urlpatterns = [
    path('', views.base_poll, name='base_poll'),
    path('add_poll/', views.add_poll, name='add_poll'),


]
