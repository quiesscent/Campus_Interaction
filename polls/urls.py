from django.urls import path
from . import views

urlpatterns = [
    path('', views.base_poll, name='base_poll'),
    path('add_polls/', views.add_polls, name='add_polls'),
    path('polls/<int:poll_id>/vote/', views.vote_poll, name='vote_poll'), 
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('polls/edit/<int:poll_id>/', views.edit_poll, name='edit_poll'),
    path('polls/delete/<int:poll_id>/', views.delete_poll, name='delete_poll'),
    path('polls/<int:poll_id>/results/', views.poll_results, name='poll_results'),  # New URL for poll results
]

