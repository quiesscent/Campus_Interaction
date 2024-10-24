from django.urls import path, include
from . import views
from .views import university_autocomplete


urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('create/', views.create_event, name='create_event'),  # This must be present
    path('university-autocomplete/', views.university_autocomplete, name='university-autocomplete'),
    path('select2/', include('django_select2.urls')),
]
