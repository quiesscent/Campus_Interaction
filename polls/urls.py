from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_polls, name='show_polls'),
]
