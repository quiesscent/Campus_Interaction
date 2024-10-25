from django.urls import path
from . import views

urlpatterns = [
    path('', views.base_poll, name='base_poll'),
    path('add_polls/', views.add_polls, name='add_polls'),
]
