from django.urls import path, include
from . import views
from .views import university_autocomplete

app_name = 'events'

urlpatterns = [
    # Main event views
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('create/', views.create_event, name='create_event'),  # Event creation

    # Event actions
    path('<int:event_id>/react/', views.toggle_reaction, name='toggle_reaction'),  # Event reactions
    path('api/university-autocomplete/', views.university_autocomplete, name='university_autocomplete'),

    # Comment-related endpoints
    path('api/events/<int:event_id>/comment/', views.add_comment, name='add_comment'),  # Add a comment to an event
    path('api/comments/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),  # Like a comment

    # Integrate select2 for dropdowns
    path('select2/', include('django_select2.urls')),
]
